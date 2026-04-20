import React from 'react';
import { login } from '../../modules/auth/service/AuthService';
import { Link } from 'react-router-dom';

const AuthInput = ({ label, ...props }: any) => (
  <div className="relative w-full mb-4">
    <input
      {...props}
      className="w-full bg-[#333] text-white h-14 px-5 pt-4 pb-1 rounded outline-none focus:bg-[#454545] transition-colors peer"
      placeholder=" "
    />
    <label className="absolute left-5 top-4 text-nfGrey-50 duration-150 transform -translate-y-3 scale-75 z-10 origin-[0] 
    peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-3
    pointer-events-none
    ">
      {label}
    </label>
  </div>
);

export default function Login() {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');

  function handleLogin() {
    login(email, password)
      .then((data) => {
        alert('Đăng nhập thành công!');
        localStorage.setItem('token', data.token);
        window.location.href = data.role === 'ADMIN' ? '/admin' : '/onboarding';
      })
      .catch((error: { message: string; }) => {
        alert('Đăng nhập thất bại: ' + error.message);
      });
  }

  return (
    <div className="relative min-h-screen w-full bg-[url('https://assets.nflxext.com/ffe/siteui/vlv3/f841d4c7-10e1-40af-bcae-07a3f8cf141a/vn-en-20220502-popsignuptwoweeks-perspective_alpha_website_medium.jpg')] bg-cover bg-no-repeat">

      <div className="absolute inset-0 bg-black/60 bg-gradient-to-t from-black via-transparent to-black" />

      <div className="relative flex justify-center items-center min-h-screen">
        <div className="bg-black/75 p-10 md:p-16 self-center w-full max-w-[450px] rounded-xl shadow-2xl">
          <h2 className="text-white text-3xl font-bold mb-8 text-center">Đăng nhập</h2>

          <form onSubmit={(e) => e.preventDefault()}>
            <AuthInput label="Email" type="email" value={email}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
            />
            <AuthInput label="Mật khẩu" type="password" value={password}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)} />

            <button className="bg-nfRed text-white font-bold w-full py-3 rounded bg-red-700 transition" onClick={handleLogin}>
              Đăng nhập
            </button>
          </form>

          <div className="mt-10 text-white text-center">
            Mới tham gia Netflix?
            <Link to="/register" className="text-white hover:underline ml-1 font-semibold">Đăng ký ngay.</Link>
          </div>
        </div>
      </div>
    </div>
  );
}

