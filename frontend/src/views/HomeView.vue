<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Document, List, Grid } from '@element-plus/icons-vue'

const router = useRouter()

const navigateTo = (path: string) => {
  router.push(path)
}
</script>

<template>
  <div class="home-view">
    <el-row :gutter="24">
      <el-col :span="24">
        <el-card class="welcome-card">
          <template #header>
            <div class="welcome-header">
              <h1>数据字典工具</h1>
              <p>统一词根、字段、模型管理平台</p>
            </div>
          </template>
          
          <div class="welcome-content">
            <p>欢迎使用数据字典工具！这是一个专为团队内部设计的数据管理平台，帮助您：</p>
            <ul>
              <li>统一管理业务词根，建立标准化的命名规范</li>
              <li>基于词根组合创建字段，确保命名的一致性和可读性</li>
              <li>构建数据模型，管理字段关系和业务逻辑</li>
              <li>支持导出和版本管理，便于团队协作</li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" style="margin-top: 24px;">
      <el-col :span="8">
        <el-card class="module-card" @click="navigateTo('/roots')">
          <div class="module-content">
            <el-icon class="module-icon" size="48" color="#409EFF">
              <Document />
            </el-icon>
            <h3>词根管理</h3>
            <p>管理业务词根，建立标准化命名规范</p>
            <ul>
              <li>词根创建、编辑、删除</li>
              <li>别名映射和标签管理</li>
              <li>使用统计和影响分析</li>
            </ul>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="module-card" @click="navigateTo('/fields')">
          <div class="module-content">
            <el-icon class="module-icon" size="48" color="#67C23A">
              <List />
            </el-icon>
            <h3>字段管理</h3>
            <p>基于词根组合创建和管理字段</p>
            <ul>
              <li>字段创建和词根组合</li>
              <li>智能命名生成</li>
              <li>查重校验和状态管理</li>
            </ul>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="module-card" @click="navigateTo('/models')">
          <div class="module-content">
            <el-icon class="module-icon" size="48" color="#E6A23C">
              <Grid />
            </el-icon>
            <h3>模型管理</h3>
            <p>构建数据模型，管理字段关系</p>
            <ul>
              <li>模型创建和配置</li>
              <li>字段绑定和排序</li>
              <li>导出SQL和Excel</li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" style="margin-top: 24px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <h3>快速开始</h3>
          </template>
          
          <el-steps :active="1" align-center>
            <el-step title="创建词根" description="先创建业务词根，如：cust（客户）、order（订单）" />
            <el-step title="组合字段" description="基于词根组合创建字段，如：cust_id、order_amount" />
            <el-step title="构建模型" description="将字段组合成数据模型，如：客户表、订单表" />
          </el-steps>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.home-view {
  padding: 20px;
}

.welcome-card {
  text-align: center;
}

.welcome-header h1 {
  margin: 0;
  color: #303133;
  font-size: 32px;
}

.welcome-header p {
  margin: 8px 0 0 0;
  color: #606266;
  font-size: 16px;
}

.welcome-content {
  text-align: left;
  max-width: 800px;
  margin: 0 auto;
}

.welcome-content p {
  color: #606266;
  line-height: 1.6;
}

.welcome-content ul {
  color: #606266;
  line-height: 1.8;
}

.module-card {
  cursor: pointer;
  transition: all 0.3s;
  height: 100%;
}

.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.module-content {
  text-align: center;
  padding: 20px 0;
}

.module-icon {
  margin-bottom: 16px;
}

.module-content h3 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 20px;
}

.module-content p {
  margin: 0 0 16px 0;
  color: #606266;
  line-height: 1.5;
}

.module-content ul {
  text-align: left;
  color: #606266;
  line-height: 1.6;
  padding-left: 20px;
}

.module-content li {
  margin-bottom: 4px;
}
</style>
