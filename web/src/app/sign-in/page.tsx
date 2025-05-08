"use client";
import Alert from "@/components/Alert";
import { loginUser, registerUser } from "@/lib/auth";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

const SignInPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [pending, setPending] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [showAlert, setShowAlert] = useState({
    show: false,
    message: "",
    type: "",
  });

  const router = useRouter(); // 获取 router 实例
  const searchParams = useSearchParams();

  const toggleAuthMode = () => {
    setIsLogin(!isLogin);
  };

  // 处理并翻译错误消息
  const processErrorMessage = (err: any): string => {
    // 如果有详细错误信息数组
    if (err.detail && Array.isArray(err.detail)) {
      const errors = err.detail.map((item: any) => {
        // 根据错误类型和位置进行翻译
        let fieldName = "";
        if (item.loc && item.loc.length > 1) {
          switch(item.loc[1]) {
            case "email": fieldName = "邮箱"; break;
            case "password": fieldName = "密码"; break;
            case "username": fieldName = "用户名"; break;
            default: fieldName = item.loc[1];
          }
        }

        // 处理特定错误类型
        if (item.type === "value_error") {
          if (item.msg.includes("email address")) {
            return `${fieldName}格式不正确: ${item.ctx?.reason || ""}`;
          }
        }

        // 如果没有特殊处理，则返回原始消息
        return `${fieldName}: ${item.msg}`;
      });
      return errors.join("\n");
    }
    
    // 如果是字符串错误
    if (typeof err === "string") {
      return err;
    }
    
    // 默认错误信息
    return "操作失败，请稍后重试";
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setPending(true);
    setError("");
    try {
      if (isLogin) {
        await loginUser(name, password);
        setShowAlert({
          show: true,
          message: "登录成功！",
          type: "success",
        });
        // 获取 returnUrl 参数
        const returnUrl = searchParams.get("returnUrl");
        router.push(returnUrl || "/"); // 登录成功后跳转到 returnUrl 或者首页
      } else {
        await registerUser(name, email, password);
        setShowAlert({
          show: true,
          message: "注册成功！",
          type: "success",
        });
        setIsLogin(true);
        // 获取 returnUrl 参数
        const returnUrl = searchParams.get("returnUrl");
        router.push(returnUrl || "/"); // 登录成功后跳转到 returnUrl 或者首页
      }
    } catch (err: any) {
      console.log(err);
      const errorMessage = processErrorMessage(err);
      setError(errorMessage);
      setShowAlert({
        show: true,
        message: isLogin ? "登录失败！" : "注册失败！\n" + errorMessage,
        type: "error",
      });
    } finally {
      setName("");
      setEmail("");
      setPassword("");
      setPending(false);
    }
  };

  // Automatically hide the alert after 2 seconds
  useEffect(() => {
    if (showAlert.show) {
      const timer = setTimeout(() => {
        setShowAlert({ ...showAlert, show: false });
      }, 5000); // 自动关闭弹窗

      return () => clearTimeout(timer); // 清除计时器，防止内存泄漏
    }
  }, [showAlert]);

  return (
    <div className="absolute w-full h-full top-0 left-0 min-h-screen flex items-center justify-center opacity-100 scrollbar-hide">
      {showAlert.show && <Alert showAlert={showAlert} />}
      <div
        className={`w-full max-w-[30%] space-y-8 p-10 bg-white rounded-xl shadow-lg z-10  opacity-80`}
      >
        <h1
          className={`text-center text-3xl font-extrabold text-transparent bg-clip-text
            bg-gradient-to-r from-indigo-500 to-indigo-700`}
        >
          LAYRA
        </h1>

        <h2 className="text-2xl font-bold text-center text-gray-700">
          {isLogin ? "登录" : "注册"}
        </h2>

        {error && (
          <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <form className="space-y-6" onSubmit={handleSubmit}>
          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium text-gray-700"
            >
              Name
            </label>
            <input
              id="name"
              name="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoComplete="name"
              required
              className={`mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-xs focus:outline-hidden focus:border-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm`}
            />
          </div>

          {!isLogin && (
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700"
              >
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="text"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                placeholder="邮箱暂不校验正确性"
                required
                className={`mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-xs focus:outline-hidden focus:border-2 focus:ring-indigo-500 focus:border-indigo-500
                     sm:text-sm`}
              />
            </div>
          )}

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700"
            >
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
              className={`mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-xs focus:outline-hidden focus:border-2 "focus:ring-indigo-500 focus:border-indigo-500"
                  focus:ring-slate-600 focus:border-slate-600 sm:text-sm`}
            />
          </div>

          <div>
            <button
              type="submit"
              className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-xs text-sm font-medium text-white
                bg-indigo-600 hover:bg-indigo-700 focus:outline-hidden focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 cursor-pointer disabled:cursor-not-allowed`}
              disabled={pending}
            >
              {pending ? "Sending" : isLogin ? "Sign In" : "Sign Up"}
            </button>
          </div>
        </form>

        <div className="text-sm text-center">
          {isLogin ? (
            <p>
              Don&apos;t have an account?{" "}
              <button
                onClick={toggleAuthMode}
                className={`font-medium text-indigo-600 hover:text-indigo-500
                     cursor-pointer disabled:cursor-not-allowed`}
                disabled={pending}
              >
                {pending ? "Sending" : "Sign Up"}
              </button>
            </p>
          ) : (
            <p>
              Already have an account?{" "}
              <button
                onClick={toggleAuthMode}
                className={`font-medium text-indigo-600 hover:text-indigo-500 cursor-pointer disabled:cursor-not-allowed`}
                disabled={pending}
              >
                {pending ? "Sending" : "Sign In"}
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

// 使用 Suspense 包裹整个页面组件
const Page = () => (
  <Suspense fallback={<div>Loading...</div>}>
    <SignInPage />
  </Suspense>
);

export default Page;
