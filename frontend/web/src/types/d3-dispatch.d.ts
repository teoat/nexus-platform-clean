declare module "d3-dispatch" {
  export function dispatch<T = any>(...types: string[]): Dispatch<T>;

  interface Dispatch<T> {
    (type: string, ...args: any[]): void;
    on(type: string, listener?: (this: T, ...args: any[]) => void): Dispatch<T>;
    call(type: string, that?: T, ...args: any[]): void;
    apply(type: string, that?: T, args?: any[]): void;
    copy(): Dispatch<T>;
  }
}
