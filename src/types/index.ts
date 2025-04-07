export interface IGoods {
  title: string
  price: number
  express: string
  remain: number
  thumb: string[]
}

export interface CardGoods {
  id: string
  title: string
  price: number
  desc: string
  num: number
  thumb: string
}

export interface Config {
  base: {
    xue: number
    lan: number
    check_dao_ju: number
  },
  scenes: Scene[]
}

export interface Scene {
  id: string
  name: string
  checked: boolean
  time: number
  keys: string[]
  sort: number
  gws: string[]
  gw_checked: string[]
  [name: string]: any
}