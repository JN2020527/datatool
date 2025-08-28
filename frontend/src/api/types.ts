// 通用响应类型
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  code?: string
}

export interface PaginationResponse<T = any> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// 词根相关类型
export interface Root {
  id: number
  name: string
  normalized_name: string
  aliases: string[]
  tags: string[]
  usage_count: number
  remark?: string
  status: 'active' | 'deprecated'
  created_at: string
  updated_at: string
}

export interface RootCreate {
  name: string
  remark?: string
  tags?: string[]
}

export interface RootUpdate {
  name?: string
  remark?: string
  tags?: string[]
  status?: 'active' | 'deprecated'
}

export interface AliasCreate {
  alias: string
}

// 字段相关类型
export interface Field {
  id: number
  field_name: string
  normalized_name: string
  meaning: string
  data_type: string
  root_list: string[]
  remark?: string
  status: 'active' | 'deprecated'
  created_at: string
  updated_at: string
}

export interface FieldCreate {
  field_name: string
  meaning: string
  data_type: string
  root_list: string[]
  remark?: string
}

export interface FieldUpdate {
  field_name?: string
  meaning?: string
  data_type?: string
  root_list?: string[]
  remark?: string
  status?: 'active' | 'deprecated'
}

export interface FieldUniqueCheck {
  field_name: string
  exclude_id?: number
}

export interface FieldUniqueResponse {
  is_unique: boolean
  suggestions?: string[]
}

// 模型相关类型
export interface Model {
  id: number
  model_name: string
  description: string
  remark?: string
  status: 'active' | 'deprecated'
  created_at: string
  updated_at: string
}

export interface ModelCreate {
  model_name: string
  description: string
  remark?: string
}

export interface ModelUpdate {
  model_name?: string
  description?: string
  remark?: string
  status?: 'active' | 'deprecated'
}

export interface ModelField {
  id: number
  field_id: number
  field_name: string
  pos: number
  required: boolean
  default_value?: string
  created_at: string
}

export interface ModelFieldBinding {
  field_id: number
  pos: number
  required: boolean
  default_value?: string
}

export interface ModelDetail {
  id: number
  model_name: string
  description: string
  remark?: string
  status: 'active' | 'deprecated'
  fields: ModelField[]
  created_at: string
  updated_at: string
}

export interface ExportFormat {
  format: 'sql' | 'csv'
  include_ddl?: boolean
  include_data?: boolean
} 