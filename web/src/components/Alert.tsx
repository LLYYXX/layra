type ShowAlert = {
  show: boolean;
  type: string;
  message: string;
};

const Alert = ({showAlert}: {showAlert: ShowAlert}) => {
  // 处理换行显示
  const formatMessage = (message: string) => {
    if (!message) return '';
    
    // 将文本中的换行符替换为<br/>标签
    const lines = message.split('\n');
    
    return lines.map((line, index) => (
      <span key={index}>
        {line}
        {index < lines.length - 1 && <br />}
      </span>
    ));
  };
  
  return (
    <div
      className={`w-1/3 z-50 fixed top-20 left-1/2 transform -translate-x-1/2 p-4 rounded-lg text-white text-center shadow-lg transition-opacity duration-300 ease-in-out ${
        showAlert.show ? "opacity-100" : "opacity-0"
      } ${
        showAlert.type === "success"
          ? "bg-gradient-to-r from-indigo-400 to-indigo-500"
          : "bg-gradient-to-r from-red-400 to-red-500"
      } 
            shadow-xl border border-gray-200 ${showAlert.type === "success" ? "animate-bounce" : ""}`}
    >
      <div className="text-lg font-semibold">{formatMessage(showAlert.message)}</div>
    </div>
  );
};

export default Alert;
