<template>
  <div class="user-manage">
    <div class="header">
      <h2>用户管理</h2>
      <div>
        <el-button type="primary" @click="showAddDialog = true">新增用户</el-button>
        <div class="search-box">
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户账号"
            prefix-icon="el-icon-search"
            @input="handleSearch"
          >
          </el-input>
        </div>
      </div>
    </div>

    <el-table
      :data="filteredUsers.slice((currentPage-1)*pageSize, currentPage*pageSize)"
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="account" label="账号"></el-table-column>
      <el-table-column prop="role" label="角色">
        <template slot-scope="scope">
          <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'success'">
            {{ scope.row.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_time" label="创建时间">
        <template slot-scope="scope">
          {{ new Date(scope.row.created_time).toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态">
        <template slot-scope="scope">
          <el-tag :type="scope.row.is_active ? 'success' : 'info'">
            {{ scope.row.is_active ? '正常' : '已禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="260">
        <template slot-scope="scope">
          <el-button
            size="mini"
            :type="scope.row.is_active ? 'warning' : 'success'"
            @click="handleToggleStatus(scope.row)"
            v-if="scope.row.role !== 'admin'"
          >
            {{ scope.row.is_active ? '禁用' : '启用' }}
          </el-button>
          <el-button
            size="mini"
            type="primary"
            @click="handleEdit(scope.row)"
          >编辑</el-button>
          <el-button
            size="mini"
            type="danger"
            @click="handleDelete(scope.row)"
            v-if="scope.row.role !== 'admin'"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      @current-change="handleCurrentChange"
      :current-page="currentPage"
      :page-size="pageSize"
      :total="filteredUsers.length"
      layout="total, prev, pager, next"
      class="pagination"
    >
    </el-pagination>

    <!-- 新增用户弹窗 -->
    <el-dialog title="新增用户" :visible.sync="showAddDialog">
      <el-form :model="addForm" :rules="addRules" ref="addForm" label-width="80px">
        <el-form-item label="账号" prop="account">
          <el-input v-model="addForm.account" placeholder="9位账号"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="addForm.password" type="password" placeholder="6-20位密码"></el-input>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="addForm.role">
            <el-radio label="user">普通用户</el-radio>
            <el-radio label="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showAddDialog = false">取 消</el-button>
        <el-button type="primary" @click="submitAdd">确 定</el-button>
      </div>
    </el-dialog>

    <!-- 编辑用户弹窗 -->
    <el-dialog title="编辑用户" :visible.sync="showEditDialog">
      <el-form :model="editForm" :rules="editRules" ref="editForm" label-width="80px">
        <el-form-item label="账号" prop="account">
          <el-input v-model="editForm.account" disabled></el-input>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="editForm.role">
            <el-radio label="user">普通用户</el-radio>
            <el-radio label="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="editForm.is_active" active-text="正常" inactive-text="禁用"></el-switch>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showEditDialog = false">取 消</el-button>
        <el-button type="primary" @click="submitEdit">保 存</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'UserManage',
  data() {
    return {
      users: [],
      loading: false,
      searchQuery: '',
      currentPage: 1,
      pageSize: 10,
      showAddDialog: false,
      showEditDialog: false,
      addForm: {
        account: '',
        password: '',
        role: 'user'
      },
      addRules: {
        account: [
          { required: true, message: '请输入账号', trigger: 'blur' },
          { min: 9, max: 9, message: '账号必须是9位', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 20, message: '密码长度6-20位', trigger: 'blur' }
        ],
        role: [
          { required: true, message: '请选择角色', trigger: 'change' }
        ]
      },
      editForm: {
        id: '',
        account: '',
        role: 'user',
        is_active: true
      },
      editRules: {
        role: [
          { required: true, message: '请选择角色', trigger: 'change' }
        ],
        is_active: [
          { required: true, message: '请选择状态', trigger: 'change' }
        ]
      }
    }
  },
  computed: {
    filteredUsers() {
      if (!this.searchQuery) return this.users
      return this.users.filter(user => 
        user.account.toLowerCase().includes(this.searchQuery.toLowerCase())
      )
    }
  },
  created() {
    this.fetchUsers()
  },
  methods: {
    async fetchUsers() {
      this.loading = true
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          this.$message.error('请先登录')
          this.$router.push('/login')
          return
        }
        const response = await request.get('/api/users/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        this.users = response.data
      } catch (error) {
        console.error('获取用户列表错误:', error)
        if (error.response && error.response.status === 401) {
          this.$message.error('登录已过期，请重新登录')
          this.$router.push('/login')
        } else {
          this.$message.error('获取用户列表失败')
        }
      } finally {
        this.loading = false
      }
    },
    async handleToggleStatus(user) {
      try {
        const action = user.is_active ? 'disable' : 'enable'
        await request.post(`/api/users/${user.id}/${action}_account/`)
        this.$message.success(`${user.is_active ? '禁用' : '启用'}成功`)
        await this.fetchUsers()
      } catch (error) {
        console.error('切换状态错误:', error)
        this.$message.error('操作失败')
      }
    },
    async handleDelete(user) {
      try {
        await this.$confirm('确认删除该用户?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await request.delete(`/api/users/${user.id}/`)
        this.$message.success('删除成功')
        await this.fetchUsers()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除用户错误:', error)
          this.$message.error('删除失败')
        }
      }
    },
    handleSearch() {
      this.currentPage = 1
    },
    handleCurrentChange(page) {
      this.currentPage = page
    },
    // 新增用户
    submitAdd() {
      this.$refs.addForm.validate(async valid => {
        if (!valid) return
        try {
          await request.post('/api/users/register/', this.addForm)
          this.$message.success('新增用户成功')
          this.showAddDialog = false
          this.$refs.addForm.resetFields()
          await this.fetchUsers()
        } catch (error) {
          this.$message.error(error.response?.data?.error || '新增失败')
        }
      })
    },
    // 编辑用户
    handleEdit(user) {
      this.editForm = { ...user }
      this.showEditDialog = true
    },
    submitEdit() {
      this.$refs.editForm.validate(async valid => {
        if (!valid) return
        try {
          await request.patch(`/api/users/${this.editForm.id}/`, {
            role: this.editForm.role,
            is_active: this.editForm.is_active
          })
          this.$message.success('修改成功')
          this.showEditDialog = false
          await this.fetchUsers()
        } catch (error) {
          this.$message.error('修改失败')
        }
      })
    }
  }
}
</script>

<style scoped>
.user-manage {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-box {
  width: 300px;
  display: inline-block;
  margin-left: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style> 