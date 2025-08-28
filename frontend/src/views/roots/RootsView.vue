<template>
  <div class="roots-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>词根管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新增词根
          </el-button>
        </div>
      </template>
      
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索词根名称"
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

      <el-table :data="roots" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="词根名称" width="200" />
        <el-table-column prop="normalized_name" label="标准化名称" width="200" />
        <el-table-column prop="usage_count" label="使用次数" width="100" />
        <el-table-column prop="tags" label="标签" width="200">
          <template #default="{ row }">
            <el-tag v-for="tag in row.tags" :key="tag" size="small" style="margin-right: 4px">
              {{ tag }}
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
            <el-button size="small" @click="editRoot(row)">编辑</el-button>
            <el-button size="small" @click="showAliasDialog(row)">别名</el-button>
            <el-button size="small" type="danger" @click="deleteRoot(row)">删除</el-button>
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

    <!-- 新增/编辑词根对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑词根' : '新增词根'"
      width="500px"
    >
      <el-form :model="rootForm" :rules="rules" ref="rootFormRef" label-width="100px">
        <el-form-item label="词根名称" prop="name">
          <el-input v-model="rootForm.name" placeholder="请输入词根名称（snake_case格式）" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="rootForm.remark" type="textarea" placeholder="请输入备注信息" />
        </el-form-item>
        <el-form-item label="标签" prop="tags">
          <el-select
            v-model="rootForm.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请选择或输入标签"
          >
            <el-option
              v-for="tag in availableTags"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
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
import { rootsApi } from '@/api'
import type { Root, RootCreate, RootUpdate } from '@/api/types'

// 响应式数据
const loading = ref(false)
const roots = ref<Root[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const statusFilter = ref('')

// 对话框相关
const dialogVisible = ref(false)
const isEdit = ref(false)
const rootFormRef = ref()
const rootForm = reactive<RootCreate & { id?: number }>({
  name: '',
  remark: '',
  tags: []
})

// 可用标签
const availableTags = ref<string[]>([])

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入词根名称', trigger: 'blur' },
    { pattern: /^[a-z][a-z0-9_]*$/, message: '词根名称必须符合snake_case格式', trigger: 'blur' }
  ]
}

// 获取词根列表
const fetchRoots = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      search: searchQuery.value || undefined,
      status: statusFilter.value || undefined
    }
    const response: any = await rootsApi.getRoots(params)
    // 简化响应处理
    if (response && response.items) {
      roots.value = response.items
      total.value = response.total || 0
    } else {
      roots.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取词根列表失败:', error)
    ElMessage.error('获取词根列表失败')
    roots.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  fetchRoots()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchRoots()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchRoots()
}

// 显示新增对话框
const showCreateDialog = () => {
  isEdit.value = false
  Object.assign(rootForm, {
    name: '',
    remark: '',
    tags: []
  })
  dialogVisible.value = true
}

// 编辑词根
const editRoot = (root: Root) => {
  isEdit.value = true
  Object.assign(rootForm, {
    id: root.id,
    name: root.name,
    remark: root.remark || '',
    tags: [...(root.tags || [])]
  })
  dialogVisible.value = true
}

// 提交词根
const submitRoot = async () => {
  if (!rootFormRef.value) return
  
  try {
    await rootFormRef.value.validate()
    
    if (isEdit.value && rootForm.id) {
      const updateData: RootUpdate = {
        name: rootForm.name,
        remark: rootForm.remark,
        tags: rootForm.tags
      }
      await rootsApi.updateRoot(rootForm.id, updateData)
      ElMessage.success('更新成功')
    } else {
      const createData: RootCreate = {
        name: rootForm.name,
        remark: rootForm.remark,
        tags: rootForm.tags
      }
      await rootsApi.createRoot(createData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchRoots()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  }
}

// 删除词根
const deleteRoot = async (root: Root) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除词根 "${root.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await rootsApi.deleteRoot(root.id)
    ElMessage.success('删除成功')
    fetchRoots()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 显示别名对话框（占位）
const showAliasDialog = (root: Root) => {
  ElMessage.info('别名功能开发中...')
}

// 初始化
onMounted(() => {
  fetchRoots()
})
</script>

<style scoped>
.roots-view {
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
</style> 