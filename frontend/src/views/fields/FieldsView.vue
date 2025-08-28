<template>
  <div class="fields-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>字段管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新增字段
          </el-button>
        </div>
      </template>
      
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索字段名称"
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
        
        <el-select v-model="rootFilter" placeholder="词根筛选" clearable @change="handleSearch">
          <el-option
            v-for="root in availableRoots"
            :key="root.name"
            :label="root.name"
            :value="root.name"
          />
        </el-select>
      </div>

      <el-table :data="fields" v-loading="loading" style="width: 100%">
        <el-table-column prop="field_name" label="字段名称" width="200" />
        <el-table-column prop="normalized_name" label="标准化名称" width="200" />
        <el-table-column prop="meaning" label="含义" width="250" />
        <el-table-column prop="data_type" label="数据类型" width="120" />
        <el-table-column prop="root_list" label="词根组合" width="200">
          <template #default="{ row }">
            <el-tag v-for="root in row.root_list" :key="root" size="small" style="margin-right: 4px">
              {{ root }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editField(row)">编辑</el-button>
            <el-button 
              size="small" 
              :type="row.status === 'active' ? 'warning' : 'success'"
              @click="toggleFieldStatus(row)"
            >
              {{ row.status === 'active' ? '停用' : '启用' }}
            </el-button>
            <el-button size="small" type="danger" @click="deleteField(row)">删除</el-button>
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

    <!-- 新增/编辑字段对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑字段' : '新增字段'"
      width="600px"
    >
      <el-form :model="fieldForm" :rules="rules" ref="fieldFormRef" label-width="100px">
        <el-form-item label="字段名称" prop="field_name">
          <el-input v-model="fieldForm.field_name" placeholder="请输入字段名称" />
        </el-form-item>
        <el-form-item label="含义" prop="meaning">
          <el-input v-model="fieldForm.meaning" type="textarea" placeholder="请描述字段的业务含义" />
        </el-form-item>
        <el-form-item label="数据类型" prop="data_type">
          <el-select v-model="fieldForm.data_type" placeholder="请选择数据类型">
            <el-option label="VARCHAR" value="VARCHAR" />
            <el-option label="INT" value="INT" />
            <el-option label="BIGINT" value="BIGINT" />
            <el-option label="DECIMAL" value="DECIMAL" />
            <el-option label="DATETIME" value="DATETIME" />
            <el-option label="BOOLEAN" value="BOOLEAN" />
          </el-select>
        </el-form-item>
        <el-form-item label="词根组合" prop="root_list">
          <el-select
            v-model="fieldForm.root_list"
            multiple
            filterable
            placeholder="请选择词根组合"
            @change="handleRootsChange"
          >
            <el-option
              v-for="root in availableRoots"
              :key="root.name"
              :label="root.name"
              :value="root.name"
            />
          </el-select>
          <div class="form-tip">
            <el-button size="small" type="text" @click="showRootCreateDialog">
              词根不足？点击创建
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="fieldForm.remark" type="textarea" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitField">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 词根创建对话框 -->
    <el-dialog
      v-model="rootDialogVisible"
      title="创建新词根"
      width="500px"
    >
      <el-form :model="rootForm" :rules="rootRules" ref="rootFormRef" label-width="100px">
        <el-form-item label="词根名称" prop="name">
          <el-input v-model="rootForm.name" placeholder="请输入词根名称（snake_case格式）" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="rootForm.remark" type="textarea" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="rootDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitRoot">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { fieldsApi, rootsApi } from '@/api'
import type { Field, FieldCreate, FieldUpdate, Root, RootCreate } from '@/api/types'

// 响应式数据
const loading = ref(false)
const fields = ref<Field[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const statusFilter = ref('')
const rootFilter = ref('')
const availableRoots = ref<Root[]>([])

// 字段对话框相关
const dialogVisible = ref(false)
const isEdit = ref(false)
const fieldFormRef = ref()
const fieldForm = reactive<FieldCreate & { id?: number; remark?: string }>({
  field_name: '',
  meaning: '',
  data_type: '',
  root_list: []
})

// 词根对话框相关
const rootDialogVisible = ref(false)
const rootFormRef = ref()
const rootForm = reactive<RootCreate>({
  name: '',
  remark: ''
})

// 表单验证规则
const rules = {
  field_name: [
    { required: true, message: '请输入字段名称', trigger: 'blur' }
  ],
  meaning: [
    { required: true, message: '请输入字段含义', trigger: 'blur' }
  ],
  data_type: [
    { required: true, message: '请选择数据类型', trigger: 'change' }
  ],
  root_list: [
    { required: true, message: '请选择词根组合', trigger: 'change' }
  ]
}

const rootRules = {
  name: [
    { required: true, message: '请输入词根名称', trigger: 'blur' },
    { pattern: /^[a-z][a-z0-9_]*$/, message: '词根名称必须符合snake_case格式', trigger: 'blur' }
  ]
}

// 获取字段列表
const fetchFields = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      search: searchQuery.value || undefined,
      status: statusFilter.value || undefined,
      root: rootFilter.value || undefined
    }
    const response: any = await fieldsApi.getFields(params)
    if (response && response.items) {
      fields.value = response.items
      total.value = response.total || 0
    } else {
      fields.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取字段列表失败:', error)
    ElMessage.error('获取字段列表失败')
    fields.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 获取可用词根
const fetchRoots = async () => {
  try {
    const response: any = await rootsApi.getRoots({ size: 1000 })
    if (response && response.items) {
      availableRoots.value = response.items
    }
  } catch (error) {
    console.error('获取词根列表失败:', error)
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  fetchFields()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchFields()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchFields()
}

// 词根组合变化处理
const handleRootsChange = () => {
  // 可以在这里添加词根组合的验证逻辑
}

// 显示新增字段对话框
const showCreateDialog = () => {
  isEdit.value = false
  Object.assign(fieldForm, {
    field_name: '',
    meaning: '',
    data_type: '',
    root_list: [],
    remark: ''
  })
  dialogVisible.value = true
}

// 编辑字段
const editField = (field: Field) => {
  isEdit.value = true
  Object.assign(fieldForm, {
    id: field.id,
    field_name: field.field_name,
    meaning: field.meaning,
    data_type: field.data_type,
    root_list: [...(field.root_list || [])],
    remark: field.remark || ''
  })
  dialogVisible.value = true
}

// 提交字段
const submitField = async () => {
  if (!fieldFormRef.value) return
  
  try {
    await fieldFormRef.value.validate()
    
    if (isEdit.value && fieldForm.id) {
      const updateData: FieldUpdate = {
        field_name: fieldForm.field_name,
        meaning: fieldForm.meaning,
        data_type: fieldForm.data_type,
        root_list: fieldForm.root_list,
        remark: fieldForm.remark
      }
      await fieldsApi.updateField(fieldForm.id, updateData)
      ElMessage.success('更新成功')
    } else {
      const createData: FieldCreate = {
        field_name: fieldForm.field_name,
        meaning: fieldForm.meaning,
        data_type: fieldForm.data_type,
        root_list: fieldForm.root_list,
        remark: fieldForm.remark
      }
      await fieldsApi.createField(createData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchFields()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  }
}

// 切换字段状态
const toggleFieldStatus = async (field: Field) => {
  try {
    const newStatus = field.status === 'active' ? 'deprecated' : 'active'
    await fieldsApi.updateFieldStatus(field.id, newStatus)
    ElMessage.success('状态更新成功')
    fetchFields()
  } catch (error) {
    console.error('状态更新失败:', error)
    ElMessage.error('状态更新失败')
  }
}

// 删除字段
const deleteField = async (field: Field) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除字段 "${field.field_name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await fieldsApi.deleteField(field.id)
    ElMessage.success('删除成功')
    fetchFields()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 显示词根创建对话框
const showRootCreateDialog = () => {
  Object.assign(rootForm, {
    name: '',
    remark: ''
  })
  rootDialogVisible.value = true
}

// 提交词根
const submitRoot = async () => {
  if (!rootFormRef.value) return
  
  try {
    await rootFormRef.value.validate()
    
    await rootsApi.createRoot(rootForm)
    ElMessage.success('词根创建成功')
    rootDialogVisible.value = false
    
    // 刷新词根列表
    await fetchRoots()
  } catch (error) {
    console.error('词根创建失败:', error)
    ElMessage.error('词根创建失败')
  }
}

// 初始化
onMounted(() => {
  fetchFields()
  fetchRoots()
})
</script>

<style scoped>
.fields-view {
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

.form-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}
</style> 