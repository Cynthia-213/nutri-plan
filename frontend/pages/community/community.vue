<template>
  <view class="page">
    <view class="status-bar" :style="{ height: statusBarHeight + 'px' }"></view>
    

    <view v-if="Object.values(showActionMenu).some(v => v)" class="action-menu-mask" @tap="closeAllActionMenus"></view>
    
    <scroll-view
      :scroll-top="scrollTopVal"
      scroll-with-animation="true"
      scroll-y
      class="list"
      @scrolltolower="loadMore"
      enhanced
      show-scrollbar="false"
    >
      <view v-if="blogs.length === 0 && !loading" class="empty-state">
        <image src="/static/empty_post.png" mode="aspectFit" class="empty-img" />
        <text>{{ viewMode === 'mine' ? '你还没有发布过动态哦' : '社区暂时空空如也' }}</text>
      </view>

      <view
        v-for="item in blogs"
        :key="item.id"
        class="card"
        :data-blog-id="item.id"
      >
        <view class="card-header">
          <view class="user-avatar-mini">{{ (item.username || 'U').charAt(0).toUpperCase() }}</view>
          <view class="user-info">
            <view class="user-name">{{ item.username || '健康用户' }}</view>
            <view class="post-time">{{ formatDate(item.created_at) }}</view>
          </view>
          <view v-if="viewMode === 'mine'" class="post-actions">
            <view class="action-menu-btn" @tap.stop="toggleActionMenu(item.id)">
              <text>⋯</text>
            </view>
            <view v-if="showActionMenu[item.id]" class="action-menu" @tap.stop>
              <view class="action-menu-item" @tap="openEdit(item)">编辑</view>
              <view class="action-menu-item" @tap="hideBlog(item)">隐藏</view>
              <view class="action-menu-item danger" @tap="deleteBlog(item)">删除</view>
            </view>
          </view>
        </view>

        <view class="card-body">
          <view class="card-title">{{ item.title }}</view>
          <view class="card-content">{{ item.content }}</view>
        </view>

        <view v-if="getImageList(item).length > 0" class="card-images" :class="'count-' + getImageList(item).length">
          <view
            v-for="(img, idx) in getImageList(item)"
            :key="idx"
            class="image-wrapper"
            @tap="handlePreviewImage(img, getImageList(item))"
          >
            <image
              :src="img"
              mode="aspectFill"
              :lazy-load="true"
              @error="handleImageError(img, idx)"
              @load="handleImageLoad(img)"
            />
            <view v-if="imageErrors[img]" class="image-error">
              <text>⚠️</text>
            </view>
          </view>
        </view>

        <view class="card-actions">
          <view class="action-btn like" @tap.stop="like(item)" :class="{ active: item.is_liked }">
            <text class="icon">{{ item.is_liked ? '❤️' : '🤍' }}</text>
            <text>{{ item.likes_count || 0 }}</text>
          </view>
          
          <view class="action-btn comment" @tap.stop="toggleComments(item)">
            <text class="icon">💬</text>
            <text>{{ item.comments_count || 0 }}</text>
          </view>
        </view>

        <!-- 评论区域 -->
        <view v-if="expandedComments[item.id]" class="comments-section">
          <!-- 评论列表 -->
          <view class="comments-list">
            <view v-if="commentsLoading[item.id]" class="comment-loading">
              <text>加载中...</text>
            </view>
            <view v-else-if="comments[item.id] && comments[item.id].length > 0">
              <view
                v-for="comment in comments[item.id]"
                :key="comment.id"
                class="comment-item"
                :id="`comment-${comment.id}`"
                :class="{ 'highlight-comment': highlightedCommentId === comment.id }"
              >
                <view class="comment-avatar">{{ (comment.username || 'U').charAt(0).toUpperCase() }}</view>
                <view class="comment-content">
                  <view class="comment-header">
                    <text class="comment-username">{{ comment.username || '用户' }}</text>
                    <text v-if="comment.parent_username" class="comment-reply-to">回复 @{{ comment.parent_username }}</text>
                    <text class="comment-time">{{ formatDate(comment.created_at) }}</text>
                  </view>
                  <text class="comment-text">{{ comment.content }}</text>
                  <view class="comment-actions">
                    <text class="comment-reply-btn" @tap="startReply(item, comment)">回复</text>
                  </view>
                </view>
              </view>
            </view>
            <view v-else class="comment-empty">
              <text>暂无评论</text>
            </view>
          </view>

          <!-- 评论输入框 -->
          <view class="comment-input-wrapper">
            <view v-if="replyingTo[item.id]" class="reply-hint">
              <text>回复 @{{ replyingTo[item.id].username }}</text>
              <text class="cancel-reply" @tap="cancelReply(item)">取消</text>
            </view>
            <input
              v-model="commentInputs[item.id]"
              class="comment-input"
              :placeholder="replyingTo[item.id] ? `回复 @${replyingTo[item.id].username}...` : '写一条评论...'"
              @confirm="submitComment(item)"
            />
            <view class="comment-send-btn" @tap="submitComment(item)">
              <text>发送</text>
            </view>
          </view>
        </view>
      </view>

      <view class="load-status">
        <view v-if="loading" class="loading-icon"></view>
        <text v-if="loading">加载中...</text>
      </view>
    </scroll-view>

    <view class="tab-bar">
      <view
        class="tab-item"
        :class="{ active: viewMode === 'public' }"
        @tap="switchMode('public')"
      >
        <view class="tab-icon">🏠</view>
        <view class="tab-label">社区</view>
      </view>

      <view class="tab-item plus-wrap" @tap="openPublish">
        <view class="plus-btn">
          <text class="plus-icon">＋</text>
        </view>
      </view>

      <view
        class="tab-item"
        :class="{ active: viewMode === 'mine' }"
        @tap="switchMode('mine')"
      >
        <view class="tab-icon">👤</view>
        <view class="tab-label">我的</view>
      </view>
    </view>

    <view v-if="publishVisible" class="popup-mask" @tap="closePublish">
      <view class="popup-panel" @tap.stop>
        <view class="popup-header">
          <text class="popup-title">新建动态</text>
          <text class="popup-close" @tap="closePublish">×</text>
        </view>
        <scroll-view class="popup-body" scroll-y>
          <view class="input-area">
            <input v-model="form.title" class="title-input" placeholder="输入标题..." placeholder-style="color:#ccc" />
            <textarea 
              v-model="form.content" 
              class="content-input" 
              placeholder="分享你的运动心得或饮食计划..." 
              maxlength="500"
            />
          </view>
          <view class="upload-section">
            <view class="u-title">添加图片 <text class="u-count">({{ images.length }}/9)</text></view>
            <view class="u-list">
              <view v-for="(img, idx) in images" :key="idx" class="u-thumb">
                <image :src="img" mode="aspectFill" />
                <view class="u-remove" @tap="removeImage(idx)">×</view>
              </view>
              <view v-if="images.length < 9" class="u-add" @tap="chooseImage">
                <text>📸</text>
              </view>
            </view>
          </view>
        </scroll-view>
        <view class="popup-footer">
          <button class="btn-cancel" @tap="closePublish">取消</button>
          <button class="btn-save" :loading="publishing" @tap="publish">发布</button>
        </view>
      </view>
    </view>

    <!-- 编辑帖子弹窗 -->
    <view v-if="editVisible" class="popup-mask" @tap="closeEdit">
      <view class="popup-panel" @tap.stop>
        <view class="popup-header">
          <text class="popup-title">编辑动态</text>
          <text class="popup-close" @tap="closeEdit">×</text>
        </view>
        <scroll-view class="popup-body" scroll-y>
          <view class="input-area">
            <input v-model="editForm.title" class="title-input" placeholder="输入标题..." placeholder-style="color:#ccc" />
            <textarea 
              v-model="editForm.content" 
              class="content-input" 
              placeholder="分享你的运动心得或饮食计划..." 
              maxlength="500"
            />
          </view>
          <view class="upload-section">
            <view class="u-title">添加图片 <text class="u-count">({{ editImages.length }}/9)</text></view>
            <view class="u-list">
              <view v-for="(img, idx) in editImages" :key="idx" class="u-thumb">
                <image :src="img" mode="aspectFill" />
                <view class="u-remove" @tap="removeEditImage(idx)">×</view>
              </view>
              <view v-if="editImages.length < 9" class="u-add" @tap="chooseEditImage">
                <text>📸</text>
              </view>
            </view>
          </view>
        </scroll-view>
        <view class="popup-footer">
          <button class="btn-cancel" @tap="closeEdit">取消</button>
          <button class="btn-save" :loading="editing" @tap="saveEdit">保存</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted, getCurrentInstance } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import api from '@/services/api'

const blogs = ref([])
const skip = ref(0)
const limit = 20
const loading = ref(false)
const noMore = ref(false)
const viewMode = ref('public') // 'public' | 'mine'
const publishVisible = ref(false)
const editVisible = ref(false)
const editing = ref(false)
const editingBlogId = ref(null)
const statusBarHeight = ref(0)
const scrollTopVal = ref(0)
const { proxy } = getCurrentInstance()

// 评论相关
const expandedComments = ref({}) // 记录哪些帖子展开了评论
const comments = ref({}) // 存储每个帖子的评论列表 { blogId: [comments] }
const commentsLoading = ref({}) // 记录哪些帖子正在加载评论
const commentInputs = ref({}) // 存储每个帖子的评论输入内容 { blogId: 'content' }
const replyingTo = ref({}) // 记录正在回复的评论 { blogId: comment }

// 操作菜单相关
const showActionMenu = ref({})

// 获取状态栏高度
onMounted(() => {
  try {
    const systemInfo = uni.getSystemInfoSync()
    statusBarHeight.value = systemInfo.statusBarHeight || 0
    // 设置 CSS 变量
    // #ifdef APP-PLUS
    if (statusBarHeight.value > 0) {
      const pages = getCurrentPages()
      if (pages.length > 0) {
        const currentPage = pages[pages.length - 1]
        if (currentPage && currentPage.$vm && currentPage.$vm.$el) {
          const el = currentPage.$vm.$el
          if (el && el.style && typeof el.style.setProperty === 'function') {
            el.style.setProperty('--status-bar-height', `${statusBarHeight.value}px`)
          }
        }
      }
    }
    // #endif
  } catch (e) {
    console.error('获取状态栏高度失败:', e)
    // 设置默认值，避免后续使用出错
    statusBarHeight.value = 0
  }
})

const form = ref({
  title: '',
  content: '',
})
const images = ref([])
const publishing = ref(false)

const editForm = ref({
  title: '',
  content: '',
})
const editImages = ref([])
const imageErrors = ref({})

const handlePreviewImage = (current, urls) => {
  uni.previewImage({ current, urls })
}

const handleImageError = (img, idx) => {
  console.error('图片加载失败:', img, idx)
  imageErrors.value[img] = true
}

const handleImageLoad = (img) => {
  // 图片加载成功，清除错误标记
  if (imageErrors.value[img]) {
    delete imageErrors.value[img]
  }
}

const formatDate = (val) => {
  if (!val) return ''
  return val.slice(0, 19).replace('T', ' ')
}

const getImageList = (item) => {
  // 优先使用 images 数组（新数据结构）
  if (item.images && Array.isArray(item.images) && item.images.length > 0) {
    return item.images.map(img => typeof img === 'string' ? img : img.image_url).filter(url => url && url.startsWith('http'))
  }
  // 兼容旧的 image_url 字符串格式
  if (item.image_url && typeof item.image_url === 'string') {
    return item.image_url.split(',').filter(Boolean).map(url => url.trim()).filter(url => url.startsWith('http'))
  }
  return []
}

const fetchBlogs = async () => {
  if (loading.value || noMore.value) return
  loading.value = true
  try {
    const res = viewMode.value === 'public'
      ? await api.getBlogs(skip.value, limit)
      : await api.getMyBlogs(skip.value, limit)
    const items = res?.items || res || []
    // 确保每个博客都有comments_count字段
    items.forEach(item => {
      if (item.comments_count === undefined) {
        item.comments_count = 0
      }
    })
    blogs.value = blogs.value.concat(items)
    skip.value += items.length
    if (items.length < limit) noMore.value = true
  } catch (e) {
    console.error('加载博客失败:', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const chooseImage = () => {
  const remain = 9 - images.value.length
  if (remain <= 0) {
    uni.showToast({ title: '最多只能上传9张图片', icon: 'none' })
    return
  }
  
  uni.chooseImage({
    count: remain,
    success: async (res) => {
      const files = res.tempFilePaths.slice(0, remain)
      
      // 先添加本地预览（显示临时路径）
      const startIdx = images.value.length
      for (const file of files) {
        images.value.push(file) // 临时使用本地路径显示预览
      }
      
      // 后台上传，逐个替换为 COS URL
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        const idx = startIdx + i
        const uploaded = await uploadToCOS(file)
        if (uploaded) {
          // 替换为 COS URL
          images.value[idx] = uploaded
        } else {
          // 上传失败，移除该项
          images.value.splice(idx, 1)
          uni.showToast({ title: `第${i + 1}张图片上传失败`, icon: 'none' })
        }
      }
    }
  })
}

const removeImage = (idx) => {
  images.value.splice(idx, 1)
}

const uploadToCOS = (filePath) => {
  const token = uni.getStorageSync('token')
  const BASE_URL = 'http://192.168.31.248:8000/api'
  
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: `${BASE_URL}/blogs/upload`,
      filePath: filePath,
      name: 'file',
      header: {
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (res) => {
        try {
          const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
          if (res.statusCode >= 200 && res.statusCode < 300) {
            console.log('上传成功:', data.file_url)
            resolve(data.file_url)
          } else {
            console.error('上传失败:', res.statusCode, data)
            uni.showToast({ title: data.detail || '上传失败', icon: 'none' })
            reject(new Error(data.detail || '上传失败'))
          }
        } catch (e) {
          console.error('解析响应失败:', e, res.data)
          uni.showToast({ title: '上传失败', icon: 'none' })
          reject(new Error('上传失败'))
        }
      },
      fail: (err) => {
        console.error('上传请求失败:', err)
        uni.showToast({ title: '上传失败', icon: 'none' })
        reject(err)
      }
    })
  })
}

const publish = async () => {
  if (!form.value.title || !form.value.content) {
    uni.showToast({ title: '标题和内容必填', icon: 'none' })
    return
  }
  
  // 检查是否有未上传完成的图片（本地临时路径）
  const localImages = images.value.filter(img => img.startsWith('file://') || img.startsWith('/'))
  if (localImages.length > 0) {
    uni.showToast({ title: '图片上传中，请稍候...', icon: 'none' })
    return
  }
  
  publishing.value = true
  try {
    // 只使用成功上传的 COS URL（以 http:// 或 https:// 开头）
    const uploadedUrls = images.value.filter(img => img && (img.startsWith('http://') || img.startsWith('https://')))
    
    await api.createBlog({ 
      ...form.value, 
      image_urls: uploadedUrls.length > 0 ? uploadedUrls : null
    })
    uni.showToast({ title: '发布成功', icon: 'success' })
    form.value = { title: '', content: '' }
    images.value = []
    blogs.value = []
    skip.value = 0
    noMore.value = false
    fetchBlogs()
    closePublish()
  } catch (e) {
    console.error('Publish error:', e)
    uni.showToast({ title: '发布失败: ' + (e.message || '未知错误'), icon: 'none', duration: 2000 })
  } finally {
    publishing.value = false
  }
}

const like = async (item) => {
  try {
    const res = await api.likeBlog(item.id)
    // 更新点赞数和点赞状态
    item.likes_count = res.likes_count
    item.is_liked = res.is_liked
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

// 切换评论展开/收起
const toggleComments = async (item) => {
  const blogId = item.id
  if (expandedComments.value[blogId]) {
    // 收起评论
    expandedComments.value[blogId] = false
  } else {
    // 展开评论，如果还没有加载过，则加载评论
    expandedComments.value[blogId] = true
    if (!comments.value[blogId]) {
      await loadComments(blogId)
    }
  }
}

// 加载评论
const loadComments = async (blogId) => {
  commentsLoading.value[blogId] = true
  try {
    const res = await api.getBlogComments(blogId)
    comments.value[blogId] = res?.items || res || []
    // 更新帖子中的评论数
    const blog = blogs.value.find(b => b.id === blogId)
    if (blog) {
      blog.comments_count = res?.total || (res?.items || res || []).length
    }
  } catch (e) {
    console.error('加载评论失败:', e)
    uni.showToast({ title: '加载评论失败', icon: 'none' })
    comments.value[blogId] = []
  } finally {
    commentsLoading.value[blogId] = false
  }
}

// 开始回复
const startReply = (item, comment) => {
  const blogId = item.id
  replyingTo.value[blogId] = comment
  // 如果回复子评论，自动添加@姓名
  if (comment.parent_id) {
    // 已经是回复，在内容前加上@父评论者
    const prefix = `@${comment.parent_username || comment.username} `
    if (!commentInputs.value[blogId] || !commentInputs.value[blogId].startsWith(prefix)) {
      commentInputs.value[blogId] = prefix
    }
  } else {
    // 回复主评论，添加@主评论者
    const prefix = `@${comment.username} `
    commentInputs.value[blogId] = prefix
  }
}

// 取消回复
const cancelReply = (item) => {
  const blogId = item.id
  replyingTo.value[blogId] = null
  commentInputs.value[blogId] = ''
}

// 提交评论
const submitComment = async (item) => {
  const blogId = item.id
  let content = (commentInputs.value[blogId] || '').trim()
  
  if (!content) {
    uni.showToast({ title: '请输入评论内容', icon: 'none' })
    return
  }
  
  // 如果正在回复，确保内容包含@姓名
  const replyTarget = replyingTo.value[blogId]
  if (replyTarget) {
    const targetName = replyTarget.parent_username || replyTarget.username
    const expectedPrefix = `@${targetName} `
    // 如果内容没有@前缀，自动添加
    if (!content.startsWith(expectedPrefix)) {
      content = expectedPrefix + content
    }
  }
  
  try {
    const commentData = {
      content: content,
      parent_id: replyTarget ? replyTarget.id : null
    }
    const newComment = await api.createBlogComment(blogId, commentData)
    // 添加到评论列表
    if (!comments.value[blogId]) {
      comments.value[blogId] = []
    }
    comments.value[blogId].push(newComment)
    // 清空输入框和回复状态
    commentInputs.value[blogId] = ''
    replyingTo.value[blogId] = null
    // 更新评论数
    if (!item.comments_count) {
      item.comments_count = 0
    }
    item.comments_count++
    uni.showToast({ title: '评论成功', icon: 'success' })
  } catch (e) {
    console.error('提交评论失败:', e)
    uni.showToast({ title: '评论失败', icon: 'none' })
  }
}

// 操作菜单相关功能
const toggleActionMenu = (blogId) => {
  // 关闭其他菜单
  Object.keys(showActionMenu.value).forEach(id => {
    if (id !== blogId) {
      showActionMenu.value[id] = false
    }
  })
  // 切换当前菜单
  showActionMenu.value[blogId] = !showActionMenu.value[blogId]
}

const closeAllActionMenus = () => {
  Object.keys(showActionMenu.value).forEach(id => {
    showActionMenu.value[id] = false
  })
}

const hideBlog = async (item) => {
  // 关闭菜单
  showActionMenu.value[item.id] = false
  
  uni.showModal({
    title: '确认隐藏',
    content: '隐藏后其他人将无法看到此帖子，确定隐藏？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await api.hideBlog(item.id)
          // 从列表中移除（如果是在公共视图）
          if (viewMode.value === 'public') {
            blogs.value = blogs.value.filter(b => b.id !== item.id)
          } else {
            // 在我的帖子视图中，更新is_public状态
            item.is_public = false
          }
          uni.showToast({ title: '已隐藏', icon: 'success' })
        } catch (e) {
          console.error('隐藏失败:', e)
          uni.showToast({ title: '隐藏失败', icon: 'none' })
        }
      }
    }
  })
}

const loadMore = () => {
  fetchBlogs()
}

fetchBlogs()

const switchMode = (mode) => {
  if (viewMode.value === mode) return
  viewMode.value = mode
  blogs.value = []
  skip.value = 0
  noMore.value = false
  fetchBlogs()
}

// 高亮评论的ID
const highlightedCommentId = ref(null)

// 处理从通知跳转过来的情况
const handleNotificationNavigation = async (notificationData) => {
  if (!notificationData || !notificationData.blog_id) return
  
  // 1. 重置状态并加载帖子列表
  loading.value = false
  blogs.value = []
  skip.value = 0
  noMore.value = false
  await fetchBlogs()
  
  // 2. 找到目标帖子
  const blog = blogs.value.find(b => b.id === notificationData.blog_id)
  if (!blog) {
    uni.showToast({
      title: '帖子未找到',
      icon: 'none'
    })
    return
  }

  // 3. 如果是评论/回复，展开并定位
  if (notificationData.type === 'comment' || notificationData.type === 'reply') {
    // 强制展开评论区 - 使用Vue的nextTick确保响应式更新
    expandedComments.value[blog.id] = true
    
    // 等待Vue响应式更新
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // 加载评论
    await loadComments(blog.id)
    
    // 如果有comment_id，定位到对应评论
    if (notificationData.comment_id) {
      // 高亮评论
      highlightedCommentId.value = notificationData.comment_id
      setTimeout(() => {
        highlightedCommentId.value = null
      }, 2000)
      
      // 等待DOM渲染完成 - 增加等待时间确保评论列表已渲染
      await new Promise(resolve => setTimeout(resolve, 800))
      
      // 使用uni.createSelectorQuery定位评论
      const query = uni.createSelectorQuery().in(proxy)
      query.select(`#comment-${notificationData.comment_id}`).boundingClientRect()
      query.select('.list').scrollOffset()
      
      query.exec((res) => {
        if (res[0] && res[1]) {
          // 计算滚动位置
          const targetTop = res[0].top + res[1].scrollTop - 150
          scrollTopVal.value = targetTop
        } else {
          console.warn('无法定位到具体评论节点，尝试定位到帖子')
          // 如果无法定位到评论，至少定位到帖子
          setTimeout(() => {
            const blogQuery = uni.createSelectorQuery().in(proxy)
            blogQuery.select(`[data-blog-id="${notificationData.blog_id}"]`).boundingClientRect()
            blogQuery.select('.list').scrollOffset()
            blogQuery.exec((blogRes) => {
              if (blogRes[0] && blogRes[1]) {
                scrollTopVal.value = blogRes[0].top + blogRes[1].scrollTop - 100
              }
            })
          }, 200)
        }
      })
    } else {
      // 没有comment_id，只定位到帖子
      await new Promise(resolve => setTimeout(resolve, 300))
      const query = uni.createSelectorQuery().in(proxy)
      query.select(`[data-blog-id="${notificationData.blog_id}"]`).boundingClientRect()
      query.select('.list').scrollOffset()
      query.exec((res) => {
        if (res[0] && res[1]) {
          scrollTopVal.value = res[0].top + res[1].scrollTop - 100
        }
      })
    }
  } else if (notificationData.type === 'like') {
    // 点赞类型，只定位到帖子
    await new Promise(resolve => setTimeout(resolve, 300))
    const query = uni.createSelectorQuery().in(proxy)
    query.select(`[data-blog-id="${notificationData.blog_id}"]`).boundingClientRect()
    query.select('.list').scrollOffset()
    query.exec((res) => {
      if (res[0] && res[1]) {
        scrollTopVal.value = res[0].top + res[1].scrollTop - 100
      }
    })
  }
}
// 监听页面显示，检查是否有通知跳转参数
onShow(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  if (currentPage && currentPage.options && currentPage.options.notification) {
    try {
      const notificationData = JSON.parse(decodeURIComponent(currentPage.options.notification))
      handleNotificationNavigation(notificationData)
    } catch (e) {
      console.error('解析通知数据失败:', e)
    }
  }
})

const openPublish = () => {
  publishVisible.value = true
}

const closePublish = () => {
  publishVisible.value = false
}

const openEdit = (item) => {
  // 关闭菜单
  showActionMenu.value[item.id] = false
  editingBlogId.value = item.id
  editForm.value = {
    title: item.title || '',
    content: item.content || '',
  }
  // 加载现有图片
  editImages.value = getImageList(item).slice() // 复制数组
  editVisible.value = true
}

const closeEdit = () => {
  editVisible.value = false
  editingBlogId.value = null
  editForm.value = { title: '', content: '' }
  editImages.value = []
}

const chooseEditImage = () => {
  const remain = 9 - editImages.value.length
  if (remain <= 0) {
    uni.showToast({ title: '最多只能添加9张图片', icon: 'none' })
    return
  }
  
  uni.chooseImage({
    count: remain,
    success: async (res) => {
      const files = res.tempFilePaths.slice(0, remain)
      
      // 先添加本地预览（显示临时路径）
      const startIdx = editImages.value.length
      for (const file of files) {
        editImages.value.push(file) // 临时使用本地路径显示预览
      }
      
      // 后台上传，逐个替换为 COS URL
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        const idx = startIdx + i
        const uploaded = await uploadToCOS(file)
        if (uploaded) {
          // 替换为 COS URL
          editImages.value[idx] = uploaded
        } else {
          // 上传失败，移除该项
          editImages.value.splice(idx, 1)
          uni.showToast({ title: `第${i + 1}张图片上传失败`, icon: 'none' })
        }
      }
    }
  })
}

const removeEditImage = (idx) => {
  editImages.value.splice(idx, 1)
}

const saveEdit = async () => {
  if (!editForm.value.title || !editForm.value.content) {
    uni.showToast({ title: '标题和内容必填', icon: 'none' })
    return
  }
  
  // 检查是否有未上传完成的图片（本地临时路径）
  const localImages = editImages.value.filter(img => img.startsWith('file://') || img.startsWith('/'))
  if (localImages.length > 0) {
    uni.showToast({ title: '图片上传中，请稍候...', icon: 'none' })
    return
  }
  
  editing.value = true
  try {
    // 只使用成功上传的 COS URL（以 http:// 或 https:// 开头）
    const uploadedUrls = editImages.value.filter(img => img && (img.startsWith('http://') || img.startsWith('https://')))
    
    await api.updateBlog(editingBlogId.value, { 
      ...editForm.value, 
      image_urls: uploadedUrls.length > 0 ? uploadedUrls : null
    })
    uni.showToast({ title: '更新成功', icon: 'success' })
    
    // 刷新列表
    blogs.value = []
    skip.value = 0
    noMore.value = false
    fetchBlogs()
    closeEdit()
  } catch (e) {
    console.error('Edit error:', e)
    uni.showToast({ title: '更新失败: ' + (e.message || '未知错误'), icon: 'none', duration: 2000 })
  } finally {
    editing.value = false
  }
}

const deleteBlog = async (item) => {
  // 关闭菜单
  showActionMenu.value[item.id] = false
  
  uni.showModal({
    title: '确认删除',
    content: '删除后不可恢复，确定删除？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await api.deleteBlog(item.id)
          blogs.value = blogs.value.filter(b => b.id !== item.id)
        } catch (e) {
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
      }
    }
  })
}
</script>

<style scoped lang="scss">
  /* 整体页面背景 */
  .page {
    height: 100vh;
    background-color: #f8f9fb;
    color: #333;
    display: flex;
    flex-direction: column;
  }
  
  /* 状态栏安全区域 */
  .status-bar {
    /* #ifdef APP-PLUS */
    min-height: 20px;
    /* #endif */
    /* #ifndef APP-PLUS */
    height: 0;
    /* #endif */
    background-color: #f8f9fb;
    flex-shrink: 0;
  }
  
  /* 列表容器 */
  .list {
    flex: 1;
    overflow-y: auto;
    padding: 30rpx 30rpx;
    padding-bottom: 140rpx; /* 为底部导航栏留出空间 */
    /* #ifdef APP-PLUS */
    padding-top: 40rpx; /* APP 环境下增加顶部间距 */
    /* #endif */
    box-sizing: border-box;
  }
  
  /* 卡片升级 */
  .card {
    background: #fff;
    border-radius: 24rpx;
    padding: 30rpx;
    margin-bottom: 24rpx;
    box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.03);
    
    .card-header {
      display: flex;
      align-items: center;
      margin-bottom: 20rpx;
      
      .user-avatar-mini {
        width: 80rpx;
        height: 80rpx;
        background: #838B8B;
        color: #fff;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 20rpx;
      }
      
      .user-name {
        font-size: 28rpx;
        font-weight: 600;
        color: #2c3e50;
      }
      
      .post-time {
        font-size: 22rpx;
        color: #999;
      }
      
      .post-actions {
        position: relative;
        margin-left: auto;
      }
      
      .action-menu-btn {
        width: 60rpx;
        height: 60rpx;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40rpx;
        color: #666;
        cursor: pointer;
      }
      
      .action-menu {
        position: absolute;
        top: 80rpx;
        right: 0;
        background: #fff;
        border-radius: 16rpx;
        box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.15);
        min-width: 160rpx;
        z-index: 101;
        overflow: hidden;
      }
      
      .action-menu-item {
        padding: 24rpx 32rpx;
        font-size: 28rpx;
        color: #333;
        border-bottom: 1rpx solid #f0f0f0;
        
        &:last-child {
          border-bottom: none;
        }
        
        &.danger {
          color: #e74c3c;
        }
      }
    }
  
    .card-title {
      font-size: 32rpx;
      font-weight: 700;
      margin-bottom: 12rpx;
    }
  
    .card-content {
      font-size: 28rpx;
      color: #4a4a4a;
      line-height: 1.6;
    }
  
    /* 图片布局优化 - 固定尺寸显示 */
    .card-images {
      margin-top: 20rpx;
      display: grid;
      gap: 10rpx;
      
      &.count-1 {
        grid-template-columns: 1fr;
        .image-wrapper {
          width: 100%;
          height: 400rpx;
        }
      }
      &.count-2 {
        grid-template-columns: 1fr 1fr;
        .image-wrapper {
          width: 100%;
          height: 300rpx;
        }
      }
      &.count-3 {
        grid-template-columns: 1fr 1fr 1fr;
        .image-wrapper {
          width: 100%;
          height: 220rpx;
        }
      }
      &.count-4,
      &.count-5,
      &.count-6,
      &.count-7,
      &.count-8,
      &.count-9 {
        grid-template-columns: repeat(3, 1fr);
        .image-wrapper {
          width: 100%;
          height: 220rpx;
        }
      }
    }
    
    .image-wrapper {
      position: relative;
      width: 100%;
      overflow: hidden;
      border-radius: 12rpx;
      background: #f5f5f5;
      
      image {
        width: 100%;
        height: 100%;
        display: block;
        border-radius: 12rpx;
      }
    }

    
    .image-error {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: rgba(0, 0, 0, 0.5);
      color: #fff;
      padding: 8rpx 16rpx;
      border-radius: 8rpx;
      font-size: 24rpx;
    }
  
    .card-actions {
      margin-top: 30rpx;
      padding-top: 20rpx;
      border-top: 1rpx solid #f2f2f2;
      display: flex;
      justify-content: flex-start;
      gap: 40rpx;
  
      .action-btn {
        display: flex;
        align-items: center;
        font-size: 26rpx;
        color: #666;
        .icon { margin-right: 8rpx; font-size: 32rpx; }
        &.active { color: #e74c3c; }
        &.comment { color: #838B8B; }
      }
    }

    /* 评论区域 */
    .comments-section {
      margin-top: 20rpx;
      padding-top: 20rpx;
      border-top: 1rpx solid #f2f2f2;
    }

    .comments-list {
      max-height: 600rpx;
      overflow-y: auto;
      margin-bottom: 20rpx;
    }

    .comment-loading,
    .comment-empty {
      text-align: center;
      padding: 40rpx 0;
      color: #999;
      font-size: 26rpx;
    }

    .comment-item {
      display: flex;
      margin-bottom: 24rpx;
      padding: 16rpx;
      background: #f8f9fa;
      border-radius: 16rpx;
      transition: all 0.3s ease;
      
      &.highlight-comment {
        background: #fff3cd;
        box-shadow: 0 0 20rpx rgba(255, 193, 7, 0.3);
        transform: scale(1.02);
      }
    }

    .comment-avatar {
      width: 60rpx;
      height: 60rpx;
      background: #838B8B;
      color: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 24rpx;
      margin-right: 16rpx;
      flex-shrink: 0;
    }

    .comment-content {
      flex: 1;
      min-width: 0;
    }

    .comment-header {
      display: flex;
      align-items: center;
      margin-bottom: 8rpx;
      gap: 12rpx;
      flex-wrap: wrap;
    }
    
    .comment-reply-to {
      font-size: 24rpx;
      color: #838B8B;
    }

    .comment-username {
      font-size: 26rpx;
      font-weight: 600;
      color: #2c3e50;
    }

    .comment-time {
      font-size: 22rpx;
      color: #999;
    }

    .comment-text {
      font-size: 28rpx;
      color: #4a4a4a;
      line-height: 1.6;
      word-break: break-word;
    }
    
    .comment-actions {
      margin-top: 12rpx;
    }
    
    .comment-reply-btn {
      font-size: 24rpx;
      color: #838B8B;
      padding: 8rpx 16rpx;
    }
    
    .reply-hint {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12rpx 16rpx;
      background: #e3f2fd;
      border-radius: 12rpx;
      margin-bottom: 12rpx;
      font-size: 24rpx;
      color: #838B8B;
    }
    
    .cancel-reply {
      color: #838B8B;
      font-size: 24rpx;
      padding: 4rpx 12rpx;
    }

    .comment-input-wrapper {
      display: flex;
      align-items: center;
      gap: 16rpx;
      padding: 16rpx;
      background: #f8f9fa;
      border-radius: 24rpx;
    }

    .comment-input {
      flex: 1;
      height: 72rpx;
      padding: 0 24rpx;
      background: #fff;
      border: 2rpx solid #e2e8f0;
      border-radius: 36rpx;
      font-size: 28rpx;
      color: #1e293b;
    }

    .comment-send-btn {
      padding: 16rpx 32rpx;
      background: #838B8B;
      color: #fff;
      border-radius: 36rpx;
      font-size: 26rpx;
      font-weight: 600;
    }
  }
  

  /* 底部导航升级 */
  .tab-bar {
    position: fixed;
    bottom: 0;
    width: 100%;
    height: calc(110rpx + env(safe-area-inset-bottom));
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    display: flex;
    box-shadow: 0 -2rpx 30rpx rgba(0,0,0,0.05);
    
    .tab-item {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding-bottom: env(safe-area-inset-bottom);
      
      .tab-icon { font-size: 40rpx; }
      .tab-label { font-size: 20rpx; margin-top: 4rpx; color: #999; }
      &.active .tab-label { color: #838B8B; font-weight: bold; }
    }
  
    .plus-wrap {
      position: relative;
      .plus-btn {
        position: absolute;
        top: -40rpx;
        width: 100rpx;
        height: 100rpx;
        background: #838B8B;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 10rpx 20rpx rgba(131, 139, 139, 0.4);
        .plus-icon { color: #fff; font-size: 60rpx; line-height: 1; margin-bottom: 4rpx; }
      }
    }
  }
  
  /* 发布弹窗美化 */
  .popup-mask {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.35);
    display: flex;
    align-items: flex-end;
    z-index: 999;
  }
  .popup-panel {
    width: 100%;
    max-height: 90vh;
    background: #fff;
    border-top-left-radius: 28rpx;
    border-top-right-radius: 28rpx;
    padding: 30rpx;
    box-shadow: 0 -6rpx 30rpx rgba(0,0,0,0.08);
  }
  .popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
    .popup-title { font-size: 34rpx; font-weight: 700; }
    .popup-close { font-size: 40rpx; color: #888; padding: 6rpx; }
  }
  .popup-body {
    max-height: 60vh;
  }
  .popup-footer {
    display: flex;
    justify-content: flex-end;
    gap: 16rpx;
    margin-top: 20rpx;
    .btn-cancel, .btn-save {
      flex: 1;
      height: 88rpx;
      line-height: 88rpx;
      font-size: 28rpx;
      border-radius: 16rpx;
    }
    .btn-cancel { background: #f5f6f7; color: #666; }
    .btn-save { background: #838B8B; color: #fff; }
  }
  .title-input {
    font-size: 36rpx;
    font-weight: bold;
    border-bottom: 1rpx solid #eee;
    padding: 20rpx 0;
    margin-bottom: 20rpx;
  }
  .content-input {
    width: 100%;
    min-height: 260rpx;
    font-size: 30rpx;
    line-height: 1.6;
  }
  .u-title { font-size: 28rpx; color: #555; }
  .u-count { color: #999; font-size: 24rpx; margin-left: 8rpx; }
  .u-list {
    display: flex;
    gap: 20rpx;
    flex-wrap: wrap;
    margin-top: 20rpx;
    
    .u-thumb {
      width: 200rpx;
      height: 200rpx;
      position: relative;
      image { width: 100%; height: 100%; border-radius: 12rpx; }
      .u-remove {
        position: absolute; top: -10rpx; right: -10rpx;
        background: #ff4757; color: #fff; width: 40rpx; height: 40rpx;
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
      }
    }
    
    .u-add {
      width: 200rpx;
      height: 200rpx;
      background: #f7f8fa;
      border: 1rpx dashed #ddd;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 50rpx;
      border-radius: 12rpx;
    }
  }
  .empty-state {
    margin-top: 120rpx;
    display: flex;
    flex-direction: column;
    align-items: center;
    color: #999;
    font-size: 28rpx;
    .empty-img { width: 300rpx; height: 300rpx; margin-bottom: 24rpx; }
  }
  
  .action-menu-mask {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 100;
    background: transparent;
  }
</style>