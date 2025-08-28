import request from '@/utils/request'
import type { Field, FieldCreate, FieldUpdate, FieldUniqueCheck, FieldUniqueResponse, PaginationResponse } from './types'

export const fieldsApi = {
  // 获取字段列表
  getFields: (params?: { page?: number; size?: number; search?: string; status?: string; root?: string }) => {
    return request.get<PaginationResponse<Field>>('/api/v1/fields', { params })
  },

  // 获取单个字段
  getField: (id: number) => {
    return request.get<Field>(`/api/v1/fields/${id}`)
  },

  // 创建字段
  createField: (data: FieldCreate) => {
    return request.post<Field>('/api/v1/fields', data)
  },

  // 更新字段
  updateField: (id: number, data: FieldUpdate) => {
    return request.put<Field>(`/api/v1/fields/${id}`, data)
  },

  // 删除字段
  deleteField: (id: number) => {
    return request.delete(`/api/v1/fields/${id}`)
  },

  // 更新字段状态
  updateFieldStatus: (id: number, status: 'active' | 'deprecated') => {
    return request.patch<Field>(`/api/v1/fields/${id}/status`, { status })
  },

  // 检查字段唯一性
  checkFieldUnique: (data: FieldUniqueCheck) => {
    return request.post<FieldUniqueResponse>('/api/v1/fields/unique-check', data)
  },

  // 根据词根查询字段
  getFieldsByRoots: (roots: string[]) => {
    return request.get<Field[]>('/api/v1/fields/by-roots', { params: { roots: roots.join(',') } })
  }
} 