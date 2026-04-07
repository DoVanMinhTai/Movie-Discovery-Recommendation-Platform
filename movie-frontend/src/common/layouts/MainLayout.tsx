import { Outlet } from "react-router-dom";
import Header from "./components/Header";
import Footer from "./components/Footer";
import Chatbot from "../../modules/chatbot/components/Chatbot";

const MainLayout = () => {
    return (<>
        <div className="bg-[#141414] min-h-screen text-white overflow-x-hidden z-[100]">
            <Header />
            <Outlet />
            <Chatbot />
            <Footer />
        </div>
    </>)
}
export default MainLayout;