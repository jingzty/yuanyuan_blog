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

      <!-- 社交链接 -->
      <div class="info-card">
        <div class="section-title">社交链接</div>
        <div v-for="(item, index) in form.social_links" :key="index" class="social-item">
          <el-input v-model="item.name" placeholder="名称" class="social-name" />
          <el-input v-model="item.url" placeholder="https://…" class="social-url" />
          <el-button type="danger" :icon="Delete" circle size="small" @click="removeSocial(index)" />
        </div>
        <p v-if="!form.social_links.length" class="empty-hint">还没有社交链接</p>
        <div class="card-actions">
          <el-button @click="addSocial">+ 添加链接</el-button>
          <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
        </div>
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
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { getProfile, updateProfile } from '@/api/profile'
import { changePassword } from '@/api/auth'

const form = reactive({
  avatar_url: '',
  nickname: '',
  bio: '',
  social_links: [],
})

const saving = ref(false)

const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})
const pwdSaving = ref(false)

function addSocial() {
  form.social_links.push({ name: '', url: '' })
}

function removeSocial(index) {
  form.social_links.splice(index, 1)
}

async function loadProfile() {
  try {
    const data = await getProfile()
    form.avatar_url = data.avatar_url || ''
    form.nickname = data.nickname || ''
    form.bio = data.bio || ''
    form.social_links = Array.isArray(data.social_links) ? data.social_links.map(s => ({ ...s })) : []
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
      social_links: form.social_links.filter(s => s.name || s.url),
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

/* 社交链接行 */
.social-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}
.social-item:last-child {
  margin-bottom: 0;
}
.social-name {
  width: 140px;
  flex-shrink: 0;
}
.social-url {
  flex: 1;
}

.empty-hint {
  font-size: 0.85rem;
  color: var(--muted-foreground);
  padding: 0.25rem 0;
  margin-bottom: 0.75rem;
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
</style>
