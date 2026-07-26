<template>
  <div>
    <!-- 页面头部 -->
    <div class="flex items-start justify-between gap-4 mb-6">
      <div class="min-w-0">
        <h1 class="text-2xl font-semibold tracking-tight text-[var(--foreground)]">个人中心</h1>
        <p class="mt-1.5 text-sm text-[var(--muted-foreground)]">管理博主资料与账号安全</p>
      </div>
    </div>

    <!-- 居中单栏 -->
    <div class="profile-wrap">
      <!-- 博主资料 -->
      <div class="info-card">
        <div class="section-title">博主资料</div>
        <el-form label-width="72px" label-position="right">
          <el-form-item label="头像">
            <div class="avatar-field">
              <div class="avatar-preview">
                <img v-if="form.avatar_url" :src="form.avatar_url" alt="头像" />
                <span v-else>{{ form.nickname?.charAt(0) || '远' }}</span>
              </div>
              <el-input v-model="form.avatar_url" placeholder="输入头像图片 URL" />
            </div>
          </el-form-item>
          <el-form-item label="昵称">
            <el-input v-model="form.nickname" placeholder="输入昵称" maxlength="20" show-word-limit />
          </el-form-item>
          <el-form-item label="简介">
            <el-input
              v-model="form.bio"
              type="textarea"
              :rows="4"
              placeholder="介绍一下自己…"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
        </el-form>
        <div class="card-actions">
          <el-button type="primary" :loading="saving" @click="onSave">保存资料</el-button>
        </div>
      </div>

      <!-- 管理员账号 -->
      <div class="info-card">
        <div class="section-title">管理员账号</div>
        <div class="current-account">
          <span class="label">当前账号：</span>
          <span class="value">{{ currentUsername }}</span>
        </div>
        <el-form label-width="72px" label-position="right">
          <el-form-item label="新账号">
            <el-input v-model="accountForm.username" placeholder="输入新的管理员账号" maxlength="64" />
          </el-form-item>
          <el-form-item label="当前密码">
            <el-input v-model="accountForm.password" type="password" show-password placeholder="输入当前密码以确认" />
          </el-form-item>
        </el-form>
        <div class="card-actions">
          <el-button type="primary" :loading="accountSaving" @click="onChangeAccount">修改账号</el-button>
        </div>
        <p class="form-hint">修改账号后需使用新账号重新登录，原账号将立即失效。</p>
      </div>

      <!-- 修改密码 -->
      <div class="info-card">
        <div class="section-title">修改密码</div>
        <el-form label-width="72px" label-position="right">
          <el-form-item label="原密码">
            <el-input v-model="pwdForm.old_password" type="password" show-password placeholder="请输入原密码" />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="至少 6 位" />
          </el-form-item>
          <el-form-item label="确认密码">
            <el-input v-model="pwdForm.confirm_password" type="password" show-password placeholder="再次输入新密码" />
          </el-form-item>
        </el-form>
        <div class="card-actions">
          <el-button type="primary" :loading="pwdSaving" @click="onChangePwd">修改密码</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getProfile, updateProfile } from '@/api/profile'
import { changePassword, changeUsername } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const currentUsername = computed(() => auth.user?.username || '—')

const form = reactive({
  avatar_url: '',
  nickname: '',
  bio: '',
})

const saving = ref(false)

const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})
const pwdSaving = ref(false)

const accountForm = reactive({
  username: '',
  password: '',
})
const accountSaving = ref(false)

async function loadProfile() {
  try {
    const data = await getProfile()
    form.avatar_url = data.avatar_url || ''
    form.nickname = data.nickname || ''
    form.bio = data.bio || ''
  } catch (e) {
    // ignore
  }
}

async function onSave() {
  saving.value = true
  try {
    await updateProfile({
      avatar_url: form.avatar_url,
      nickname: form.nickname,
      bio: form.bio,
    })
    ElMessage.success('保存成功')
  } catch (e) {
    // error handled by interceptor
  } finally {
    saving.value = false
  }
}

async function onChangePwd() {
  if (!pwdForm.old_password || !pwdForm.new_password) {
    ElMessage.warning('请填写原密码和新密码')
    return
  }
  if (pwdForm.new_password.length < 6) {
    ElMessage.warning('新密码长度至少 6 位')
    return
  }
  if (pwdForm.new_password !== pwdForm.confirm_password) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  pwdSaving.value = true
  try {
    await changePassword({
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password,
    })
    ElMessage.success('密码修改成功')
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    pwdForm.confirm_password = ''
  } catch (e) {
    // error handled by interceptor
  } finally {
    pwdSaving.value = false
  }
}

async function onChangeAccount() {
  const newUsername = (accountForm.username || '').trim()
  if (!newUsername) {
    ElMessage.warning('请输入新账号')
    return
  }
  if (newUsername.length < 3 || newUsername.length > 64) {
    ElMessage.warning('账号长度需在 3-64 个字符之间')
    return
  }
  if (newUsername === auth.user?.username) {
    ElMessage.warning('新账号不能与当前账号相同')
    return
  }
  if (!accountForm.password) {
    ElMessage.warning('请输入当前密码以确认操作')
    return
  }
  accountSaving.value = true
  try {
    const data = await changeUsername({
      username: newUsername,
      password: accountForm.password,
    })
    // 同步更新本地 store
    if (auth.user) {
      auth.user.username = data?.username || newUsername
    }
    ElMessage.success('账号修改成功，下次请使用新账号登录')
    accountForm.username = ''
    accountForm.password = ''
  } catch (e) {
    // error handled by interceptor
  } finally {
    accountSaving.value = false
  }
}

onMounted(loadProfile)
</script>

<style scoped>
/* 居中单栏 */
.profile-wrap {
  max-width: 640px;
}

/* 卡片 */
.info-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}
.info-card:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--foreground);
  margin-bottom: 1.25rem;
}

/* 头像字段：预览 + 输入框横排 */
.avatar-field {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  width: 100%;
}
.avatar-preview {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  border: 1px solid var(--border);
  background: var(--secondary);
  display: flex;
  align-items: center;
  justify-content: center;
}
.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-preview span {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--muted-foreground);
}
.avatar-field :deep(.el-input) {
  flex: 1;
}

/* 卡片底部操作 */
.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}

/* 当前账号展示 */
.current-account {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 0.875rem;
  background: var(--secondary);
  border-radius: var(--radius-md);
  margin-bottom: 1.25rem;
}
.current-account .label {
  font-size: 0.85rem;
  color: var(--muted-foreground);
}
.current-account .value {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--foreground);
  font-family: 'Fira Code', monospace;
}

/* 表单提示 */
.form-hint {
  margin-top: 0.75rem;
  font-size: 0.8rem;
  color: var(--muted-foreground);
}
</style>
