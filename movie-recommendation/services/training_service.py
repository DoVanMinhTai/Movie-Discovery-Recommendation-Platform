from datetime import datetime
import time, os

from sklearn.base import defaultdict
from requests import Session
from common.database import SessionLocal
from model.model_registry import Model_Registry, Training_Jobs_Logs
from services.content_based_service import ContentBasedService as cbs

class ReTrainingService:
    def __init__(self, db: Session):
        self.db = db

    def train_model(self,job_id: str):
        
        timestamp = int(time.time())
        model_path = os.path.join(settings.model_base, f"model_{timestamp}.pkl")
        
        start_total = time.perf_counter()

        new_job = Training_Jobs_Logs(
            id=job_id,
            job_status="RUNNING"
        )
        db = SessionLocal()
        db.add(new_job)
        db.commit()
        
        try:
            start_cb = time.perf_counter()
            success_cb = collaborative_reTraining(db, str(model_path))
            end_cb = time.perf_counter()
            cb_duration = end_cb - start_cb
            
            new_job.collaborative_time = round(cb_duration,2)
            db.commit()
            
            if not success_cb:
                raise Exception("collaborative filtering retraining failed")
            
            start_content = time.perf_counter()
            success_content = cbs.content_based_filtering_reTraining(db, settings.model_base)
            end_content = time.perf_counter()
            content_duration = end_content - start_content
            new_job.content_based_time = round(content_duration,2)
            
            if not success_content:
                raise Exception("Content based filtering retraining failed")        
        
            new_job.status = "COMPLETED"
            new_job.total_time = round(time.perf_counter() - start_total, 2)
        except Exception as e:
            db.rollback()
            new_job.job_status = "FAILED"
            new_job.error_message = str(e)
        finally:
            db.commit()
            db.close()  



    def collaborative_reTraining(self, db: Session, model_path: str):
        
        query = "SELECT user_id, movie_id, score from ratings"
        if db.bind is None:
            print("Database engine (bind) is not configured.")
            return False
        
        try:
            df = pd.read_sql(query, db.bind)
        except Exception as e:
            print(f"Error reading from database: {e}")
            return False
        
        if df.empty:
            print("No data to train on")
            return False
        
        '''Should I pre processing in the df?
                Depend the choose ML Library 
        '''
        reader = Reader(rating_scale=(1,5))

        data = sp.Dataset.load_from_df(df[['user_id','movie_id','score']],reader)
        
        trainset, testset = train_test_split(data, test_size=0.2, random_state=42)
        
        '''Called model and train'''
        svd = sp.SVD()
        svd.fit(trainset)
        
        '''Validated Model, Should I saved model
                if model is failure or accuracy low,...
                    Don't need save it'''
        '''Accuracy,...'''
        new_metrics = evaluate_performance(svd,  testset)
        
        # get the current active model
        active_model = db.query(Model_Registry).filter(Model_Registry.is_active == True).first()
        
        should_activate_new_model = False
        
        if active_model:
            '''Compare new model with active model'''
            if new_metrics["RMSE"] < active_model.rmse:
                '''New model is better, deactivate old model'''
                active_model.is_active = False
                db.commit()
                should_activate_new_model = True
        else:
            '''No active model, activate new model'''
            should_activate_new_model = True
            
        '''Saved Model in path '''
        save_model(svd,model_path)
        
        '''Insert model_registry object to DB'''
        model_registry = Model_Registry(
            model_name = "SVD",
            version = 1.0,
            model_path = model_path,
            rmse = new_metrics["RMSE"],
            mae = new_metrics["MAE"],
            precision = new_metrics["Precision@10"],
            recall = new_metrics["Recall@10"],
            f1_score = new_metrics["F1-Score@10"],
            is_active = should_activate_new_model,
            created_at = datetime.utcnow()
        )
        '''Insert to Model Table'''
        insert_model_to_db(db, model_registry)
        
        return True

    def insert_model_to_db(self, db: Session, model_registry: Model_Registry):

        db.add(model_registry)
        db.commit()
        db.refresh(model_registry)
        
        if model_registry.id:
            print(f"Model registered with ID: {model_registry.id}")
        else:
            print("Failed to register model.")
            
    def get_top_n(predicsions,n = 10):
        
        top_n = defaultdict(list)
        for uid, iid, true_r, est, _ in predicsions:
            top_n[uid].append((iid,est,true_r))
            
        for uid, user_ratings in top_n.items():
            user_ratings.sort(key= lambda x: x[1],reverse=True)
            top_n[uid] = user_ratings[:n]
            
        return top_n

    def precision_recall_f1(predictions,k ,threshold):
        
        top_n = get_top_n(predictions,n= k)
        precisions = defaultdict(float)
        recalls = defaultdict(float)
        f1_scores = defaultdict(float)
        
        for uid, user_ratings in top_n.items():
            all_user_ratings = [p for p in predictions if p.uid == uid]
            
            '''True positives + False negatives'''
            n_rel = sum((p.r_ui > threshold ) for p in predictions if p.uid == uid)
            
            '''True positives'''
            n_rec_rel = sum((true_r > threshold) for (iid, est, true_r) in user_ratings)
            
            # Top N
            n_rec = len(user_ratings)
            
            precisions[uid] = n_rec_rel / n_rec if n_rec != 0 else 0
            
            recalls[uid] = n_rec_rel / n_rel if n_rel != 0 else 0
            
            if(precisions[uid] + recalls[uid] > 0):
                f1_scores[uid] = 2*(precisions[uid] * recalls[uid])/ (precisions[uid] + recalls[uid])
            else:
                0
        
        if len(precisions) == 0: return 0.0, 0.0, 0.0
        
        return (
            sum(precisions.values()) / len(precisions),
            sum(recalls.values()) / len(recalls),
            sum(f1_scores.values()) / len(f1_scores)
        )
            
    def evaluate_performance(svd, testset):
        predictions = svd.test(testset)
        
        rmse = sp.accuracy.rmse(predictions, verbose=False)
        mae = sp.accuracy.mae(predictions, verbose=False)
        P, R, F1 = precision_recall_f1(predictions, k=10, threshold=3.5)

        print("\n### Model Evaluation Summary ###")
        print(f"| Metric | Value | Interpretation |")
        print(f"| :--- | :---: | :--- |")
        print(f"| **RMSE** | {rmse:.4f} | Average error in predicting the rating (lower is better) |")
        print(f"| **MAE** | {mae:.4f} | Average absolute error in rating prediction (lower is better) |")
        print(f"| **Precision@10** | {P:.4f} | Percentage of Top-10 recommendations that were relevant |")
        print(f"| **Recall@10** | {R:.4f} | Percentage of all relevant items that were found in the Top-10 list |")
        print(f"| **F1-Score@10** | {F1:.4f} | Harmonic Mean of Precision and Recall (best balance) |")
        print("--------------------------------------------------")
        
        # Return Json object if needed
        return {
            "RMSE": rmse,
            "MAE": mae,
            "Precision@10": P,
            "Recall@10": R,
            "F1-Score@10": F1
        }

    def save_model(svd, path):
        if not path:
            raise ValueError("Model path must be provided to save the model.")
        
        fileName = f"model_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        full_path = os.path.join(path, fileName)
        sp.dump.dump(full_path, algorithm=svd)
        return full_path
    # Content Based Filtering Re-Training
    def content_based_filtering_reTraining(self, db: Session, mode_dir: str):
        
            query = "Select movies.movie_id,genres.name,movies.title, movies.overview  from movies Inner join movie_genres on movies.movie_id = movie_genres.movie_id INNER join genres on movie_genres.genre_id = genres.id"
            if db.bind is None:
                print("Database engine (bind) is not configured.")
                return False
            try:
                df = pd.read_sql(query,db.bind)
            except Exception as e:
                print(f"Error executing query: {e}")
                return False
            
            if df.empty:
                print("No data to train on")
                return False
            
            '''Preprocessing DataFrame'''
            title = df["title"].fillna("").astype(str)
            overview = df["overview"].fillna("").astype(str)
            name = df["name"].fillna("").astype(str)
            
            df["content"] = title + " " + overview + " " + name
            df["content"] = df["content"].fillna("").astype("str")
            
            '''Create TF-IDF Matrix'''
            tfidf = TfidfVectorizer(stop_words="english")
            tfidf_matrix = tfidf.fit_transform(df["content"])
            
            '''Compute Cosine Similarity'''
            cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
            
            file_path_sim = f"{mode_dir}/cosine_sim.pkl"
            file_path_df = f"{mode_dir}/content_df.pkl"
            
            '''Save Model Artifacts'''
            with open(file_path_sim, "wb") as f:
                import pickle
                pickle.dump(cosine_sim, f)
            with open(file_path_df, "wb") as f:
                import pickle
                pickle.dump(df, f)
                
            '''Insert to Model Registry''' 
            model_registry = Model_Registry(
                model_name="content_based_filtering",
                version=1.0,
                model_path=mode_dir,
                rmse=0.0,
                mae=0.0,
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                is_active=True
            )
            
            insert_model_to_db(db, model_registry)
            
            return {"status": "Content-based filtering model trained and saved successfully."}
            