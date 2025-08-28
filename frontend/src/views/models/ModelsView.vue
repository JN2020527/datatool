<template>
  <div class="models-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>模型管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新增模型
          </el-button>
        </div>
      </template>
      
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索模型名称"
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="handleSearch">
          <el-option label="启用" value="active" />
          <el-option label="停用" value="deprecated" />
        </el-select>
      </div>

      <el-table :data="models" v-loading="loading" style="width: 100%">
        <el-table-column prop="model_name" label="模型名称" width="200" />
        <el-table-column prop="description" label="描述" width="300" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewModelDetail(row)">查看</el-button>
            <el-button size="small" @click="editModel(row)">编辑</el-button>
            <el-button size="small" @click="showFieldBindingDialog(row)">字段</el-button>
            <el-button size="small" @click="exportModel(row)">导出</el-button>
            <el-button size="small" type="danger" @click="deleteModel(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑模型对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑模型' : '新增模型'"
      width="500px"
    >
      <el-form :model="modelForm" :rules="rules" ref="modelFormRef" label-width="100px">
        <el-form-item label="模型名称" prop="model_name">
          <el-input v-model="modelForm.model_name" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="modelForm.description" type="textarea" placeholder="请描述模型的业务用途" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="modelForm.remark" type="textarea" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitModel">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 模型详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="`模型详情 - ${currentModel?.model_name}`"
      width="800px"
    >
      <div v-if="currentModel" class="model-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="模型名称">{{ currentModel.model_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentModel.status === 'active' ? 'success' : 'danger'">
              {{ currentModel.status === 'active' ? '启用' : '停用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ currentModel.description }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ currentModel.remark || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentModel.created_at }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ currentModel.updated_at }}</el-descriptions-item>
        </el-descriptions>

        <div class="fields-section">
          <h4>字段列表</h4>
          <el-table :data="currentModel.fields" style="width: 100%">
            <el-table-column prop="pos" label="序号" width="80" />
            <el-table-column prop="field_name" label="字段名称" width="200" />
            <el-table-column prop="required" label="必填" width="80">
              <template #default="{ row }">
                <el-tag :type="row.required ? 'danger' : 'info'">
                  {{ row.required ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="default_value" label="默认值" width="150" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="small" type="danger" @click="unbindField(row)">
                  解绑
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>

    <!-- 字段绑定对话框 -->
    <el-dialog
      v-model="fieldBindingDialogVisible"
      :title="`字段绑定 - ${currentModel?.model_name}`"
      width="800px"
    >
      <div v-if="currentModel" class="field-binding">
        <div class="binding-section">
          <h4>绑定新字段</h4>
          <el-form :model="fieldBindingForm" :rules="fieldBindingRules" ref="fieldBindingFormRef" label-width="100px">
            <el-form-item label="选择字段" prop="field_id">
              <el-select
                v-model="fieldBindingForm.field_id"
                placeholder="请选择要绑定的字段"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="field in availableFields"
                  :key="field.id"
                  :label="`${field.field_name} (${field.meaning})`"
                  :value="field.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="序号" prop="pos">
              <el-input-number v-model="fieldBindingForm.pos" :min="1" />
            </el-form-item>
            <el-form-item label="必填" prop="required">
              <el-switch v-model="fieldBindingForm.required" />
            </el-form-item>
            <el-form-item label="默认值" prop="default_value">
              <el-input v-model="fieldBindingForm.default_value" placeholder="请输入默认值" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="bindField">绑定字段</el-button>
            </el-form-item>
          </el-form>
        </div>

        <div class="current-fields">
          <h4>当前字段</h4>
          <el-table :data="currentModel.fields" style="width: 100%">
            <el-table-column prop="pos" label="序号" width="80" />
            <el-table-column prop="field_name" label="字段名称" width="200" />
            <el-table-column prop="required" label="必填" width="80">
              <template #default="{ row }">
                <el-tag :type="row.required ? 'danger' : 'info'">
                  {{ row.required ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="default_value" label="默认值" width="150" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="small" type="danger" @click="unbindField(row)">
                  解绑
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>

    <!-- 导出对话框 -->
    <el-dialog
      v-model="exportDialogVisible"
      title="导出模型"
      width="400px"
    >
      <el-form :model="exportForm" label-width="100px">
        <el-form-item label="导出格式">
          <el-radio-group v-model="exportForm.format">
            <el-radio label="sql">SQL</el-radio>
            <el-radio label="csv">CSV</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="包含DDL" v-if="exportForm.format === 'sql'">
          <el-switch v-model="exportForm.include_ddl" />
        </el-form-item>
        <el-form-item label="包含数据" v-if="exportForm.format === 'sql'">
          <el-switch v-model="exportForm.include_data" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="exportDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmExport">确定导出</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { modelsApi, fieldsApi } from '@/api'
import type { Model, ModelCreate, ModelUpdate, ModelDetail, ModelFieldBinding, ExportFormat, Field } from '@/api/types'

// 响应式数据
const loading = ref(false)
const models = ref<Model[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const statusFilter = ref('')

// 对话框相关
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const fieldBindingDialogVisible = ref(false)
const exportDialogVisible = ref(false)
const isEdit = ref(false)

// 表单相关
const modelFormRef = ref()
const fieldBindingFormRef = ref()
const modelForm = reactive<ModelCreate & { id?: number; remark?: string }>({
  model_name: '',
  description: '',
  remark: ''
})

const fieldBindingForm = reactive<ModelFieldBinding>({
  field_id: 0,
  pos: 1,
  required: false,
  default_value: ''
})

const exportForm = reactive<ExportFormat>({
  format: 'sql',
  include_ddl: true,
  include_data: false
})

// 当前模型和可用字段
const currentModel = ref<ModelDetail | null>(null)
const availableFields = ref<Field[]>([])

// 表单验证规则
const rules = {
  model_name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入模型描述', trigger: 'blur' }
  ]
}

const fieldBindingRules = {
  field_id: [
    { required: true, message: '请选择字段', trigger: 'change' }
  ],
  pos: [
    { required: true, message: '请输入序号', trigger: 'blur' }
  ]
}

// 获取模型列表
const fetchModels = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      search: searchQuery.value || undefined,
      status: statusFilter.value || undefined
    }
    const response: any = await modelsApi.getModels(params)
    if (response && response.items) {
      models.value = response.items
      total.value = response.total || 0
    } else {
      models.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取模型列表失败:', error)
    ElMessage.error('获取模型列表失败')
    models.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 获取可用字段
const fetchAvailableFields = async () => {
  try {
    const response: any = await fieldsApi.getFields({ size: 1000, status: 'active' })
    if (response && response.items) {
      availableFields.value = response.items
    }
  } catch (error) {
    console.error('获取字段列表失败:', error)
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  fetchModels()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchModels()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchModels()
}

// 显示新增模型对话框
const showCreateDialog = () => {
  isEdit.value = false
  Object.assign(modelForm, {
    model_name: '',
    description: '',
    remark: ''
  })
  dialogVisible.value = true
}

// 编辑模型
const editModel = (model: Model) => {
  isEdit.value = true
  Object.assign(modelForm, {
    id: model.id,
    model_name: model.model_name,
    description: model.description,
    remark: model.remark || ''
  })
  dialogVisible.value = true
}

// 提交模型
const submitModel = async () => {
  if (!modelFormRef.value) return
  
  try {
    await modelFormRef.value.validate()
    
    if (isEdit.value && modelForm.id) {
      const updateData: ModelUpdate = {
        model_name: modelForm.model_name,
        description: modelForm.description,
        remark: modelForm.remark
      }
      await modelsApi.updateModel(modelForm.id, updateData)
      ElMessage.success('更新成功')
    } else {
      const createData: ModelCreate = {
        model_name: modelForm.model_name,
        description: modelForm.description,
        remark: modelForm.remark
      }
      await modelsApi.createModel(createData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchModels()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  }
}

// 查看模型详情
const viewModelDetail = async (model: Model) => {
  try {
    const response: any = await modelsApi.getModelDetail(model.id)
    currentModel.value = response
    detailDialogVisible.value = true
  } catch (error) {
    console.error('获取模型详情失败:', error)
    ElMessage.error('获取模型详情失败')
  }
}

// 显示字段绑定对话框
const showFieldBindingDialog = async (model: Model) => {
  try {
    const response: any = await modelsApi.getModelDetail(model.id)
    currentModel.value = response
    fieldBindingDialogVisible.value = true
  } catch (error) {
    console.error('获取模型详情失败:', error)
    ElMessage.error('获取模型详情失败')
  }
}

// 绑定字段
const bindField = async () => {
  if (!fieldBindingFormRef.value || !currentModel.value) return
  
  try {
    await fieldBindingFormRef.value.validate()
    
    await modelsApi.bindField(currentModel.value.id, fieldBindingForm)
    ElMessage.success('字段绑定成功')
    
    // 刷新模型详情
    const response: any = await modelsApi.getModelDetail(currentModel.value.id)
    currentModel.value = response
    
    // 重置表单
    Object.assign(fieldBindingForm, {
      field_id: 0,
      pos: 1,
      required: false,
      default_value: ''
    })
  } catch (error) {
    console.error('字段绑定失败:', error)
    ElMessage.error('字段绑定失败')
  }
}

// 解绑字段
const unbindField = async (field: any) => {
  if (!currentModel.value) return
  
  try {
    await ElMessageBox.confirm(
      `确定要解绑字段 "${field.field_name}" 吗？`,
      '确认解绑',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await modelsApi.unbindField(currentModel.value.id, field.field_id)
    ElMessage.success('字段解绑成功')
    
    // 刷新模型详情
    const response: any = await modelsApi.getModelDetail(currentModel.value.id)
    currentModel.value = response
  } catch (error) {
    if (error !== 'cancel') {
      console.error('字段解绑失败:', error)
      ElMessage.error('字段解绑失败')
    }
  }
}

// 导出模型
const exportModel = (model: Model) => {
  currentModel.value = { ...model, fields: [] } as ModelDetail
  Object.assign(exportForm, {
    format: 'sql',
    include_ddl: true,
    include_data: false
  })
  exportDialogVisible.value = true
}

// 确认导出
const confirmExport = async () => {
  if (!currentModel.value) return
  
  try {
    await modelsApi.exportModel(currentModel.value.id, exportForm)
    ElMessage.success('导出成功')
    exportDialogVisible.value = false
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 删除模型
const deleteModel = async (model: Model) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模型 "${model.model_name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await modelsApi.deleteModel(model.id)
    ElMessage.success('删除成功')
    fetchModels()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 初始化
onMounted(() => {
  fetchModels()
  fetchAvailableFields()
})
</script>

<style scoped>
.models-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 16px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.model-detail {
  padding: 20px 0;
}

.fields-section {
  margin-top: 20px;
}

.fields-section h4 {
  margin-bottom: 16px;
  color: #303133;
}

.field-binding {
  padding: 20px 0;
}

.binding-section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.binding-section h4,
.current-fields h4 {
  margin-bottom: 16px;
  color: #303133;
}
</style> 