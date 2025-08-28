import request from '@/utils/request'
import type { Root, RootCreate, RootUpdate, AliasCreate, PaginationResponse } from './types'

export const rootsApi = {
  // 获取词根列表
  getRoots: (params?: { page?: number; size?: number; search?: string; status?: string }) => {
    return request.get<PaginationResponse<Root>>('/api/v1/roots', { params })
  },

  // 获取单个词根
  getRoot: (id: number) => {
    return request.get<Root>(`/api/v1/roots/${id}`)
  },

  // 创建词根
  createRoot: (data: RootCreate) => {
    return request.post<Root>('/api/v1/roots', data)
  },

  // 更新词根
  updateRoot: (id: number, data: RootUpdate) => {
    return request.put<Root>(`/api/v1/roots/${id}`, data)
  },

  // 删除词根
  deleteRoot: (id: number) => {
    return request.delete(`/api/v1/roots/${id}`)
  },

  // 添加别名
  addAlias: (id: number, data: AliasCreate) => {
    return request.post<Root>(`/api/v1/roots/${id}/aliases`, data)
  },

  // 获取词根影响分析
  getRootImpact: (id: number) => {
    return request.get(`/api/v1/roots/${id}/impact`)
  }
} 