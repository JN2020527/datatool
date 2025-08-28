import request from '@/utils/request'
import type { Model, ModelCreate, ModelUpdate, ModelDetail, ModelFieldBinding, ExportFormat, PaginationResponse } from './types'

export const modelsApi = {
  // 获取模型列表
  getModels: (params?: { page?: number; size?: number; search?: string; status?: string }) => {
    return request.get<PaginationResponse<Model>>('/api/v1/models', { params })
  },

  // 获取单个模型
  getModel: (id: number) => {
    return request.get<Model>(`/api/v1/models/${id}`)
  },

  // 获取模型详情（包含字段）
  getModelDetail: (id: number) => {
    return request.get<ModelDetail>(`/api/v1/models/${id}/detail`)
  },

  // 创建模型
  createModel: (data: ModelCreate) => {
    return request.post<Model>('/api/v1/models', data)
  },

  // 更新模型
  updateModel: (id: number, data: ModelUpdate) => {
    return request.put<Model>(`/api/v1/models/${id}`, data)
  },

  // 删除模型
  deleteModel: (id: number) => {
    return request.delete(`/api/v1/models/${id}`)
  },

  // 绑定字段到模型
  bindField: (modelId: number, data: ModelFieldBinding) => {
    return request.post(`/api/v1/models/${modelId}/fields`, data)
  },

  // 从模型解绑字段
  unbindField: (modelId: number, fieldId: number) => {
    return request.delete(`/api/v1/models/${modelId}/fields`, { data: { field_id: fieldId } })
  },

  // 导出模型
  exportModel: (modelId: number, format: ExportFormat) => {
    return request.post(`/api/v1/models/${modelId}/export`, format)
  }
} 