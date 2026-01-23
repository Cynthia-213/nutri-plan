<template>
  <view class="notifications-page">
    <view class="status-bar" :style="{ height: statusBarHeight + 'px' }"></view>
    
    <!-- 顶部导航栏 -->
    <view class="header">
      <view class="header-left" @tap="goBack">
        <text class="back-icon">‹</text>
      </view>
      <view class="header-title">全部互动消息</view>
      <view class="header-right" @tap="showMoreMenu">
        <text class="more-icon">⋯</text>
      </view>
    </view>

    <!-- 通知列表 -->
    <scroll-view class="notification-list" scroll-y @scrolltolower="loadMore">
      <view v-if="loading && notifications.length === 0" class="loading-wrapper">
        <text>加载中...</text>
      </view>
      <view v-else-if="notifications.length === 0" class="empty-state">
        <text>暂无通知</text>
      </view>
      <view v-else>
        <view
          v-for="notification in notifications"
          :key="notification.id"
          class="notification-item"
          :class="{ unread: !notification.is_read }"
          @tap="handleNotificationClick(notification)"
        >
          <view class="notification-avatar">
            {{ (notification.from_username || 'U').charAt(0).toUpperCase() }}
          </view>
          <view class="notification-content">
            <view class="notification-header">
              <text class="notification-username">{{ notification.from_username || '用户' }}</text>
              <text class="notification-time">{{ formatTime(notification.created_at) }}</text>
            </view>
            <view class="notification-body">
              <text class="notification-text">{{ getNotificationText(notification) }}</text>
            </view>
          </view>
          <view class="notification-thumbnail" v-if="getBlogThumbnail(notification)">
            <image :src="getBlogThumbnail(notification)" mode="aspectFill" />
          </view>
        </view>
      </view>
      
      <view v-if="loading && notifications.length > 0" class="load-more">
        <text>加载中...</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import api from '@/services/api'

const statusBarHeight = ref(0)
const notifications = ref([])
const blogThumbnails = ref({}) // 存储博客ID对应的缩略图
const loading = ref(false)
const skip = ref(0)
const limit = 50
const noMore = ref(false)

// 获取状态栏高度
onMounted(() => {
  try {
    const systemInfo = uni.getSystemInfoSync()
    statusBarHeight.value = systemInfo.statusBarHeight || 0
  } catch (e) {
    console.error('获取状态栏高度失败:', e)
  }
  loadNotifications()
})

onShow(() => {
  // 每次显示页面时刷新未读通知
  loadNotifications(true)
})

const goBack = () => {
  uni.navigateBack()
}

const showMoreMenu = () => {
  uni.showActionSheet({
    itemList: ['全部已读'],
    success: (res) => {
      if (res.tapIndex === 0) {
        markAllAsRead()
      }
    }
  })
}

const formatTime = (val) => {
  if (!val) return ''
  const date = new Date(val)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  
  // 超过7天显示具体日期
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours()
  const minute = date.getMinutes()
  return `${month}月${day}日 ${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`
}

const getNotificationText = (notification) => {
  const content = notification.content || ''
  
  switch (notification.type) {
    case 'like':
      return '赞了你的动态'
    case 'comment':
      return `评论了你的动态：${content}`
    case 'reply':
      return `回复了你的评论：${content}`
    default:
      return '你有新的通知'
  }
}

const getBlogThumbnail = (notification) => {
  if (!notification.blog_id) return null
  return blogThumbnails.value[notification.blog_id] || null
}

// 加载博客缩略图
const loadBlogThumbnails = async (blogIds) => {
  if (!blogIds || blogIds.length === 0) return
  
  try {
    // 批量获取博客信息
    for (const blogId of blogIds) {
      if (blogThumbnails.value[blogId]) continue // 已加载过
      
      try {
        const blog = await api.getBlogDetail(blogId)
        if (blog) {
          // 获取第一张图片作为缩略图
          if (blog.images && blog.images.length > 0) {
            blogThumbnails.value[blogId] = blog.images[0].image_url
          } else if (blog.image_url) {
            // 兼容旧格式
            const urls = blog.image_url.split(',').filter(Boolean)
            if (urls.length > 0) {
              blogThumbnails.value[blogId] = urls[0].trim()
            }
          }
        }
      } catch (e) {
        console.error(`加载博客${blogId}缩略图失败:`, e)
      }
    }
  } catch (e) {
    console.error('批量加载博客缩略图失败:', e)
  }
}

const loadNotifications = async (refresh = false) => {
  if (loading.value) return
  if (refresh) {
    skip.value = 0
    noMore.value = false
  }
  if (noMore.value && !refresh) return
  
  loading.value = true
  try {
    const res = await api.getNotifications({ skip: skip.value, limit: limit })
    const items = res?.items || []
    
    if (refresh) {
      notifications.value = items
    } else {
      notifications.value = notifications.value.concat(items)
    }
    
    skip.value += items.length
    if (items.length < limit) {
      noMore.value = true
    }
    
    // 加载博客缩略图
    const blogIds = items.filter(item => item.blog_id).map(item => item.blog_id)
    if (blogIds.length > 0) {
      loadBlogThumbnails(blogIds)
    }
  } catch (e) {
    console.error('加载通知失败:', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  if (!loading.value && !noMore.value) {
    loadNotifications()
  }
}

const handleNotificationClick = async (notification) => {
  // 标记为已读
  if (!notification.is_read) {
    try {
      await api.markNotificationRead(notification.id)
      notification.is_read = true
    } catch (e) {
      console.error('标记通知已读失败:', e)
    }
  }
  
  // 跳转到社区页面，并传递通知数据
  if (notification.blog_id) {
    const notificationData = encodeURIComponent(JSON.stringify({
      blog_id: notification.blog_id,
      comment_id: notification.comment_id,
      type: notification.type
    }))
    
    uni.navigateTo({
      url: `/pages/community/community?notification=${notificationData}`,
      fail: (err) => {
        console.error('跳转失败:', err)
        uni.showToast({
          title: '跳转失败',
          icon: 'none'
        })
      }
    })
  }
}

const markAllAsRead = async () => {
  try {
    await api.markAllNotificationsRead()
    notifications.value.forEach(n => n.is_read = true)
    uni.showToast({ title: '已全部标记为已读', icon: 'success' })
  } catch (e) {
    console.error('标记全部已读失败:', e)
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}
</script>

<style scoped lang="scss">
.notifications-page {
  min-height: 100vh;
  background-color: #fff;
  display: flex;
  flex-direction: column;
}

.status-bar {
  background-color: #fff;
  flex-shrink: 0;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 32rpx;
  background-color: #fff;
  border-bottom: 1rpx solid #f0f0f0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left,
.header-right {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  font-size: 56rpx;
  color: #333;
  font-weight: 300;
  line-height: 1;
}

.more-icon {
  font-size: 40rpx;
  color: #333;
  line-height: 1;
}

.header-title {
  flex: 1;
  text-align: center;
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
}

.notification-list {
  flex: 1;
  background-color: #fff;
}

.loading-wrapper,
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 100rpx 0;
  color: #999;
  font-size: 28rpx;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  padding: 32rpx;
  border-bottom: 1rpx solid #f5f5f5;
  background-color: #fff;
  
  &.unread {
    background-color: #f8f9ff;
  }
}

.notification-avatar {
  width: 96rpx;
  height: 96rpx;
  background: #838B8B;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 36rpx;
  margin-right: 24rpx;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.notification-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.notification-username {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.notification-time {
  font-size: 24rpx;
  color: #999;
  margin-left: 16rpx;
}

.notification-body {
  margin-top: 4rpx;
}

.notification-text {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
  word-break: break-word;
}

.notification-thumbnail {
  width: 120rpx;
  height: 120rpx;
  margin-left: 24rpx;
  border-radius: 12rpx;
  overflow: hidden;
  flex-shrink: 0;
  background-color: #f5f5f5;
  
  image {
    width: 100%;
    height: 100%;
  }
}

.load-more {
  text-align: center;
  padding: 40rpx 0;
  color: #999;
  font-size: 26rpx;
}
</style>
