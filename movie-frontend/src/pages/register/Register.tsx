import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { existEmail, register } from "../../modules/auth/service/AuthService";

const AuthInput = ({ label, ...props }: any) => (
  <div className="relative w-full mb-4">
    <input
      {...props}
      className="w-full bg-[#333] text-white h-[60px] px-5 pt-4 pb-1 rounded outline-none focus:bg-[#454545] border-b-2 border-transparent focus:border-b-[#e87c03] transition-all peer"
      placeholder=" "
    />
    <label className="absolute left-5 top-4 text-[#8c8c8c] duration-150 transform -translate-y-3 scale-75 z-10 origin-[0] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-3 pointer-events-none">
      {label}
    </label>
  </div>
);

export default function Register() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  function handleRegister() {
    existEmail(email)
      .then((exists) => {
        if (exists) {
          alert('Email đã tồn tại. Vui lòng sử dụng email khác.');
        } else {
          doRegister();
        }
      })
      .catch((error: { message: string; }) => {
        alert('Đã xảy ra lỗi: ' + error.message);
      });
  }

  function doRegister() {
    if (!username || !email || !password) {
      alert('Vui lòng điền tất cả các trường.');
      return;
    }
    register(username, email, password)
      .then(() => {
        alert('Đăng ký thành công!');
        navigate('/login');
      })
      .catch((error: { message: string; }) => {
        alert('Đăng ký thất bại: ' + error.message);
      });
  }

  return (
    <div className="relative min-h-screen w-full bg-[url('https://assets.nflxext.com/ffe/siteui/vlv3/f841d4c7-10e1-40af-bcae-07a3f8cf141a/vn-en-20220502-popsignuptwoweeks-perspective_alpha_website_medium.jpg')] bg-cover bg-no-repeat">

      <div className="absolute inset-0 bg-black/60 bg-gradient-to-t from-black via-transparent to-black" />

      <div className="relative flex justify-center items-center min-h-screen px-4">
        <div className="bg-black/80 p-10 md:p-16 self-center w-full max-w-[450px] rounded-xl shadow-2xl">

          <h1 className="text-white text-3xl font-bold mb-8 text-center">Đăng ký</h1>

          <div className="flex flex-col space-y-4">
            <AuthInput
              label="Tên người dùng"
              type="text"
              value={username}
              onChange={(e: any) => setUsername(e.target.value)}
            />

            <AuthInput
              label="Địa chỉ email"
              type="email"
              value={email}
              onChange={(e: any) => setEmail(e.target.value)}
            />

            <AuthInput
              label="Mật khẩu"
              type="password"
              value={password}
              onChange={(e: any) => setPassword(e.target.value)}
            />

            <button
              onClick={handleRegister}
              className="bg-[#e50914] text-white text-xl font-bold px-8 py-4 rounded mt-4 hover:bg-[#c11119] transition-all active:scale-[0.98] flex items-center justify-center">
              Đăng ký
            </button>
          </div>

          <div className="mt-10 text-[#737373] text-center">
            Bạn đã có tài khoản?
            <Link to="/login" className="text-white hover:underline ml-1 font-semibold">
              Đăng nhập ngay.
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}