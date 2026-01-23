<template>
  <view class="page">
    <view class="status-bar" :style="{ height: statusBarHeight + 'px' }"></view>
    
    <view class="header-card">
      <view class="title-row">
        <text class="title">运动热量榜</text>
        <view class="period-pill">
          <view 
            v-for="p in periods" :key="p.value"
            class="pill-item" :class="{ active: currentPeriod === p.value }"
            @tap="switchPeriod(p.value)"
          >{{ p.label }}</view>
        </view>
      </view>

      <scroll-view class="category-scroll" scroll-x show-scrollbar="false" enhanced>
        <view class="category-box">
          <view 
            class="cat-item" :class="{ active: currentCategory === null }"
            @tap="switchCategory(null)"
          >全站榜</view>
          <view 
            v-for="id in identities" :key="id.value"
            class="cat-item" :class="{ active: currentCategory === id.value }"
            @tap="switchCategory(id.value)"
          >{{ id.label }}</view>
        </view>
      </scroll-view>
    </view>

    <scroll-view scroll-y class="main-content" enhanced>
      
      <view class="podium-section" v-if="rankings.length >= 3">
        <view class="podium-item silver">
          <view class="avatar-wrap">
            <view class="avatar-box silver-border">{{ rankings[1].username ? rankings[1].username[0] : 'U' }}</view>
            <view class="medal">🥈</view>
          </view>
          <text class="p-name">{{ rankings[1].username || '未知用户' }}</text>
          <text class="p-kcal">{{ rankings[1].calories || 0 }} <text class="unit">kcal</text></text>
        </view>
        
        <view class="podium-item gold">
          <view class="avatar-wrap">
            <view class="crown">👑</view>
            <view class="avatar-box gold-border">{{ rankings[0].username ? rankings[0].username[0] : 'U' }}</view>
            <view class="medal">🥇</view>
          </view>
          <text class="p-name">{{ rankings[0].username || '未知用户' }}</text>
          <text class="p-kcal">{{ rankings[0].calories || 0 }} <text class="unit">kcal</text></text>
        </view>
        
        <view class="podium-item bronze">
          <view class="avatar-wrap">
            <view class="avatar-box bronze-border">{{ rankings[2].username ? rankings[2].username[0] : 'U' }}</view>
            <view class="medal">🥉</view>
          </view>
          <text class="p-name">{{ rankings[2].username || '未知用户' }}</text>
          <text class="p-kcal">{{ rankings[2].calories || 0 }} <text class="unit">kcal</text></text>
        </view>
      </view>

      <view class="list-container">
        <view v-if="loading && rankings.length === 0" class="empty-hint">数据加载中...</view>
        <view v-else-if="rankings.length === 0" class="empty-hint">暂无排名数据</view>
        <view v-else-if="displayRankings.length === 0 && rankings.length > 0" class="empty-hint">暂无更多排名数据</view>
        
        <view 
          v-for="(item, index) in displayRankings" 
          :key="'rank-' + (item.user_id || index)"
          class="rank-row"
          :class="{ 'is-me': item.user_id === currentUserId }"
        >
          <view class="row-rank">{{ item.rank }}</view>
          <view class="row-avatar">{{ item.username ? item.username[0] : 'U' }}</view>
          <view class="row-info">
            <text class="row-user">{{ item.username || '未知用户' }}</text>
            <text class="row-tag">{{ getIdentityLabel(item.identity) }}</text>
          </view>
          <view class="row-data">
            <text class="val">{{ item.calories || 0 }}</text>
            <text class="unit">kcal</text>
          </view>
        </view>
        <view style="height: 300rpx;"></view>
      </view>
    </scroll-view>

    <view class="fixed-user-bar" v-if="userRanking">
      <view class="u-rank-info">
        <text class="u-num">{{ userRanking.rank || '--' }}</text>
        <text class="u-label">我的排名</text>
      </view>
      <view class="u-avatar-wrap">
        <view class="u-avatar">{{ (currentUserName || 'U')[0] }}</view>
      </view>
      <view class="u-stats">
        <text class="u-name">加油，{{ currentUserName }}！</text>
      </view>
      <view class="u-btn" @tap="goToSport">去运动</view>
    </view>
  </view>
</template>

<script>
import api from '@/services/api'

export default {
  data() {
    return {
      statusBarHeight: 0,
      currentPeriod: 'day', // day, month, year
      currentCategory: null, // null表示总榜，否则是身份类型
      rankings: [],
      userRanking: null,
      loading: false,
      currentUserId: null,
      currentUserName: null,
      periods: [
        { value: 'day', label: '日榜' },
        { value: 'month', label: '月榜' },
        { value: 'year', label: '年榜' }
      ],
      identities: [
        { value: 'student', label: '学生族' },
        { value: 'office_worker', label: '职场办公人' },
        { value: 'flexible', label: '自由职业' },
        { value: 'fitness_pro', label: '健身达人' },
        { value: 'health_care', label: '康养人群' }
      ]
    }
  },
  computed: {
    currentCategoryLabel() {
      if (this.currentCategory === null) {
        return '全站'
      }
      const identity = this.identities.find(i => i.value === this.currentCategory)
      return identity ? identity.label : '全站'
    },
    displayRankings() {
      // 如果数据少于3个，显示所有数据；如果大于等于3个，只显示第4名及以后的
      if (this.rankings.length < 3) {
        return this.rankings
      }
      return this.rankings.slice(3)
    }
  },
  async onLoad() {
    // 获取状态栏高度
    const systemInfo = uni.getSystemInfoSync()
    this.statusBarHeight = systemInfo.statusBarHeight || 0
    
    // 获取当前用户信息
    await this.loadCurrentUser()
    
    this.loadRankings()
  },
  methods: {
    async loadCurrentUser() {
      try {
        const userInfo = await api.getMe()
        if (userInfo) {
          this.currentUserId = userInfo.id
          this.currentUserName = userInfo.username
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
      }
    },
    switchPeriod(period) {
      if (this.currentPeriod !== period) {
        this.currentPeriod = period
        this.loadRankings()
      }
    },
    switchCategory(category) {
      if (this.currentCategory !== category) {
        this.currentCategory = category
        this.loadRankings()
      }
    },
    async loadRankings() {
      this.loading = true
      try {
        const params = {
          period: this.currentPeriod,
          limit: 50
        }
        
        if (this.currentCategory) {
          params.identity = this.currentCategory
        }
        
        const response = await api.getRankings(params)
        console.log('排行榜API响应:', response)
        
        if (response) {
          // 确保 rankings 是数组
          this.rankings = Array.isArray(response.rankings) ? response.rankings : []
          this.userRanking = response.user_ranking || null
          
          // 如果user_ranking中有user_id，更新currentUserId
          if (this.userRanking && this.userRanking.user_id) {
            this.currentUserId = this.userRanking.user_id
          }
          
          console.log('排行榜数据:', this.rankings)
          console.log('排行榜数据长度:', this.rankings.length)
          console.log('显示列表数据:', this.displayRankings)
          console.log('显示列表数据长度:', this.displayRankings ? this.displayRankings.length : 0)
          console.log('用户排名:', this.userRanking)
        } else {
          this.rankings = []
          this.userRanking = null
        }
      } catch (error) {
        console.error('加载排行榜失败:', error)
        this.rankings = []
        this.userRanking = null
        uni.showToast({
          title: '加载失败，请重试',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },
    goToSport() {
      uni.switchTab({
        url: '/pages/exercise-tracker/exercise-tracker'
      })
    },
    getRankClass(rank) {
      if (rank === 1) return 'rank-gold'
      if (rank === 2) return 'rank-silver'
      if (rank === 3) return 'rank-bronze'
      return ''
    },
    getRankIcon(rank) {
      if (rank === 1) return '🥇'
      if (rank === 2) return '🥈'
      if (rank === 3) return '🥉'
      return ''
    },
    getIdentityLabel(identity) {
      const identityMap = {
        'student': '学生',
        'office_worker': '办公',
        'flexible': '自由',
        'fitness_pro': '健身',
        'health_care': '康养'
      }
      return identityMap[identity] || ''
    }
  }
}
</script>

<style scoped>
.page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8fafc;
}

/* 顶部卡片 */
.header-card {
  background: #ffffff;
  padding: 20rpx 0 30rpx 0;
  border-radius: 0 0 48rpx 48rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.03);
  z-index: 100;
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40rpx;
  margin-bottom: 30rpx;
  
  .title {
    font-size: 40rpx;
    font-weight: 800;
    color: #1e293b;
    letter-spacing: 1px;
  }
}

/* 周期切换 */
.period-pill {
  display: flex;
  background: #f1f5f9;
  padding: 8rpx;
  border-radius: 100rpx;
  
  .pill-item {
    padding: 12rpx 28rpx;
    font-size: 24rpx;
    color: #64748b;
    border-radius: 100rpx;
    transition: all 0.3s ease;
    
    &.active {
      background: #838B8B;
      color: #ffffff;
      box-shadow: 0 4rpx 12rpx rgba(131, 139, 139, 0.3);
    }
  }
}

/* 身份分类横滑 */
.category-box {
  display: flex;
  /* 增加左右内边距，确保滑到最左/最右时，卡片不贴边 */
  padding: 0 40rpx 10rpx 40rpx; 
  
  .cat-item {
    flex-shrink: 0;
    padding: 12rpx 32rpx;
    margin-right: 20rpx; /* 使用统一的右间距 */
    font-size: 26rpx;
    background: #f8fafc;
    color: #64748b;
    border-radius: 40rpx;
    border: 2rpx solid #f1f5f9;
    
    /* 移除之前的 last-child 特殊逻辑，靠 parent 的 padding 解决 */
    /* &:last-child {
      margin-right: 80rpx; 
    } */
    
    &.active {
      color: #838B8B;
      background: #ffffff;
      border-color: #838B8B;
      font-weight: bold;
      box-shadow: 0 4rpx 12rpx rgba(131, 139, 139, 0.1);
    }
  }
}

/* 领奖台 */
.podium-section {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  /* 增加顶部的 padding，由 80rpx 提升至 120rpx，拉开呼吸感 */
  padding: 120rpx 0 60rpx 0; 
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  
  .podium-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 210rpx;
    
    .avatar-wrap {
      position: relative;
      margin-bottom: 16rpx;
      
      .avatar-box {
        width: 110rpx;
        height: 110rpx;
        background: #e2e8f0;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40rpx;
        font-weight: bold;
        color: #fff;
        border: 4rpx solid #fff;
      }
      
      .medal {
        position: absolute;
        bottom: -10rpx;
        right: -10rpx;
        font-size: 44rpx;
      }
    }

    &.gold {
      width: 260rpx;
      transform: translateY(-20rpx);
      .avatar-box { width: 140rpx; height: 140rpx; font-size: 50rpx; background: #6366f1; }
      .gold-border { border-color: #fbbf24; border-width: 6rpx; }
      .crown { font-size: 40rpx; margin-bottom: -10rpx; z-index: 1; }
      .p-name { font-size: 32rpx; font-weight: 800; }
    }
    
    &.silver .avatar-box { background: #94a3b8; border-color: #cbd5e1; }
    &.bronze .avatar-box { background: #b45309; border-color: #fed7aa; }

    .p-name { font-size: 28rpx; color: #1e293b; margin-top: 10rpx; max-width: 180rpx; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;}
    .p-kcal { font-size: 26rpx; color: #ef4444; font-weight: 800; margin-top: 4rpx; }
    .unit { font-size: 20rpx; margin-left: 4rpx; font-weight: normal; }
  }
}

/* 列表区 */
.list-container {
  padding: 0 32rpx;
}

.rank-row {
  display: flex;
  align-items: center;
  padding: 24rpx 30rpx;
  background: #ffffff;
  border-radius: 32rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.02);
  
  &.is-me {
    background: #f0f9ff;
    border: 2rpx solid #bae6fd;
  }

  .row-rank { width: 60rpx; font-size: 30rpx; font-weight: 800; color: #94a3b8; font-style: italic; }
  .row-avatar { width: 80rpx; height: 80rpx; background: #838B8B; border-radius: 50%; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 20rpx; }
  
  .row-info {
    flex: 1;
    .row-user { font-size: 30rpx; font-weight: 600; color: #1e293b; display: block; }
    .row-tag { font-size: 20rpx; color: #838B8B; background: rgba(131,139,139,0.1); padding: 2rpx 12rpx; border-radius: 6rpx; }
  }

  .row-data {
    text-align: right;
    .val { font-size: 32rpx; font-weight: 800; color: #1e293b; }
    .unit { font-size: 22rpx; color: #94a3b8; margin-left: 6rpx; }
  }
}

/* 底部悬浮条 */
.fixed-user-bar {
  position: fixed;
  bottom: 30rpx;
  left: 32rpx;
  right: 32rpx;
  height: 128rpx;
  background: #1e293b;
  border-radius: 64rpx;
  display: flex;
  align-items: center;
  padding: 0 32rpx;
  box-shadow: 0 20rpx 48rpx rgba(0,0,0,0.25);
  z-index: 1000;
  
  .u-rank-info {
    text-align: center;
    margin-right: 24rpx;
    .u-num { color: #fff; font-size: 40rpx; font-weight: 800; display: block; line-height: 1; }
    .u-label { color: #94a3b8; font-size: 18rpx; }
  }

  .u-avatar { width: 80rpx; height: 80rpx; background: #838B8B; border-radius: 50%; border: 4rpx solid rgba(255,255,255,0.1); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: bold; }

  .u-stats {
    flex: 1;
    margin-left: 20rpx;
    .u-name { color: #fff; font-size: 26rpx; font-weight: bold; display: block; }
    .u-val { color: #94a3b8; font-size: 22rpx; }
  }

  .u-btn {
    background: #838B8B;
    color: #fff;
    padding: 16rpx 32rpx;
    border-radius: 40rpx;
    font-size: 24rpx;
    font-weight: bold;
    &:active { transform: scale(0.95); }
  }
}

.empty-hint {
  text-align: center;
  padding: 100rpx 0;
  color: #94a3b8;
  font-size: 28rpx;
}

.category-scroll {
  width: 100%;
  white-space: nowrap; /* 必须加！确保内部的 cat-item 不会换行 */
  background: #ffffff;
  padding: 10rpx 0;    /* 上下留点呼吸空间 */
}

</style>