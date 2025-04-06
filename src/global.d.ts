interface Window {
  airscript: {
    call: (key: string, value: string) => void; // 根据实际返回类型调整
  };
  [name: string]: any
}