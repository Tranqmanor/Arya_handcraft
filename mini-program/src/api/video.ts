// 视频相关接口
import { http } from './request'

export interface VideoItem {
  id: number
  title: string
  description: string
  video_url: string
  cover_url: string
  duration: number // 秒
  view_count: number
  sort_order: number
  created_at: string
}

export interface VideoViewResult {
  video_id: number
  view_count: number
  viewed: boolean
}

export function getVideos() {
  return http.get<VideoItem[]>('/videos')
}

export function getVideo(id: number) {
  return http.get<VideoItem>(`/videos/${id}`)
}

export function reportVideoView(video_id: number, viewer_key: string) {
  return http.post<VideoViewResult>(
    `/videos/${video_id}/view`,
    { viewer_key },
    false, // 游客也可观看,不带 token 也行(带也行)
  )
}