// 轮播图相关接口
import { http } from './request'

export interface CarouselImageItem {
  id: number
  image_url: string
  title: string
  description: string
  sort_order: number
  created_at: string
}

export function getCarouselImages() {
  return http.get<CarouselImageItem[]>('/carousel')
}