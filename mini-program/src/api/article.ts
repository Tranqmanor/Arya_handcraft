// 文章相关接口
import { http } from './request'

export interface ArticleListItem {
  id: number
  title: string
  summary: string
  cover_url: string
  category: string
  view_count: number
  sort_order: number
  created_at: string
}

export interface ArticleDetail extends ArticleListItem {
  content: string
  updated_at: string
}

export interface ArticleViewResult {
  article_id: number
  view_count: number
  viewed: boolean
}

export function getArticles() {
  return http.get<ArticleListItem[]>('/articles')
}

export function getArticle(id: number) {
  return http.get<ArticleDetail>(`/articles/${id}`)
}

export function reportArticleView(article_id: number) {
  return http.post<ArticleViewResult>(`/articles/${article_id}/view`, {})
}