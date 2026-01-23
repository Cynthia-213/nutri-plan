"""
排行榜服务 - 使用Redis Sorted Set实现实时排行榜
"""
import redis
from datetime import datetime, date
from typing import List, Optional, Dict, Tuple
from app.db.redis_client import get_redis
from app.models.user import User


class RankingService:
    """排行榜服务类"""
    
    # 身份分类映射
    IDENTITY_MAP = {
        'student': 'student',
        'office_worker': 'office_worker',
        'flexible': 'flexible',
        'fitness_pro': 'fitness_pro',
        'health_care': 'health_care'
    }
    
    def __init__(self):
        self.redis_client = get_redis()
    
    def _get_rank_key(self, period: str, identity: Optional[str] = None, time_str: str = None) -> str:
        """
        生成排行榜Redis Key
        :param period: 周期类型 ('day', 'month', 'year')
        :param identity: 身份类型，None表示总榜
        :param time_str: 时间字符串，格式为 YYYYMMDD (日), YYYYMM (月), YYYY (年)
        :return: Redis Key
        """
        if identity:
            return f"rank:category:{identity}:{period}:{time_str}"
        else:
            return f"rank:global:{period}:{time_str}"
    
    def _get_time_string(self, target_date: date, period: str) -> str:
        """
        根据周期类型生成时间字符串
        :param target_date: 目标日期
        :param period: 周期类型 ('day', 'month', 'year')
        :return: 时间字符串
        """
        if period == 'day':
            return target_date.strftime('%Y%m%d')
        elif period == 'month':
            return target_date.strftime('%Y%m')
        elif period == 'year':
            return target_date.strftime('%Y')
        else:
            raise ValueError(f"Invalid period: {period}")
    
    def update_ranking(self, user_id: int, calories: float, user_identity: str, log_date: date):
        """
        更新排行榜（使用Pipeline批量更新）
        :param user_id: 用户ID
        :param calories: 消耗的热量
        :param user_identity: 用户身份
        :param log_date: 记录日期
        """
        import time
        pipeline = self.redis_client.pipeline()
        
        # 生成时间字符串
        day_str = self._get_time_string(log_date, 'day')
        month_str = self._get_time_string(log_date, 'month')
        year_str = self._get_time_string(log_date, 'year')
        
        # 更新总榜（日、月、年）
        # 使用zincrby累加热量，Redis会自动处理排序
        pipeline.zincrby(self._get_rank_key('day', None, day_str), calories, str(user_id))
        pipeline.zincrby(self._get_rank_key('month', None, month_str), calories, str(user_id))
        pipeline.zincrby(self._get_rank_key('year', None, year_str), calories, str(user_id))
        
        # 更新身份分榜（日、月、年）
        if user_identity in self.IDENTITY_MAP:
            pipeline.zincrby(self._get_rank_key('day', user_identity, day_str), calories, str(user_id))
            pipeline.zincrby(self._get_rank_key('month', user_identity, month_str), calories, str(user_id))
            pipeline.zincrby(self._get_rank_key('year', user_identity, year_str), calories, str(user_id))
        
        # 设置过期时间（日榜7天，月榜2个月，年榜1年）
        pipeline.expire(self._get_rank_key('day', None, day_str), 7 * 24 * 3600)
        pipeline.expire(self._get_rank_key('month', None, month_str), 60 * 24 * 3600)
        pipeline.expire(self._get_rank_key('year', None, year_str), 365 * 24 * 3600)
        
        if user_identity in self.IDENTITY_MAP:
            pipeline.expire(self._get_rank_key('day', user_identity, day_str), 7 * 24 * 3600)
            pipeline.expire(self._get_rank_key('month', user_identity, month_str), 60 * 24 * 3600)
            pipeline.expire(self._get_rank_key('year', user_identity, year_str), 365 * 24 * 3600)
        
        pipeline.execute()
    
    def get_top_rankings(
        self, 
        period: str, 
        limit: int = 10, 
        identity: Optional[str] = None,
        target_date: Optional[date] = None
    ) -> List[Dict]:
        """
        获取排行榜Top N
        :param period: 周期类型 ('day', 'month', 'year')
        :param limit: 返回数量
        :param identity: 身份类型，None表示总榜
        :param target_date: 目标日期，None则使用当前日期
        :return: 排行榜列表，每个元素包含 user_id, calories, rank
        """
        if target_date is None:
            target_date = date.today()
        
        time_str = self._get_time_string(target_date, period)
        key = self._get_rank_key(period, identity, time_str)
        
        # 获取Top N，WITHSCORES返回分数
        results = self.redis_client.zrevrange(key, 0, limit - 1, withscores=True)
        
        rankings = []
        for rank, (user_id_str, score) in enumerate(results, start=1):
            # 从score中提取实际热量（去掉时间戳部分的影响）
            # 由于时间戳部分很小，直接取整数部分即可
            calories = int(score)
            rankings.append({
                'user_id': int(user_id_str),
                'calories': calories,
                'rank': rank
            })
        
        return rankings
    
    def get_user_ranking(
        self,
        user_id: int,
        period: str,
        identity: Optional[str] = None,
        target_date: Optional[date] = None
    ) -> Optional[Dict]:
        """
        获取用户排名和分数
        :param user_id: 用户ID
        :param period: 周期类型 ('day', 'month', 'year')
        :param identity: 身份类型，None表示总榜
        :param target_date: 目标日期，None则使用当前日期
        :return: 包含 rank 和 calories 的字典，如果用户不在榜上则返回None
        """
        if target_date is None:
            target_date = date.today()
        
        time_str = self._get_time_string(target_date, period)
        key = self._get_rank_key(period, identity, time_str)
        
        # 获取排名（从0开始，需要+1）
        rank = self.redis_client.zrevrank(key, str(user_id))
        if rank is None:
            return None
        
        # 获取分数
        score = self.redis_client.zscore(key, str(user_id))
        if score is None:
            return None
        
        calories = int(score)
        
        return {
            'user_id': user_id,
            'rank': rank + 1,  # 排名从1开始
            'calories': calories
        }
    
    def update_user_identity(
        self,
        user_id: int,
        old_identity: str,
        new_identity: str,
        target_date: Optional[date] = None
    ):
        """
        更新用户身份时，从旧分榜移除，添加到新分榜
        :param user_id: 用户ID
        :param old_identity: 旧身份
        :param new_identity: 新身份
        :param target_date: 目标日期，None则使用当前日期
        """
        if target_date is None:
            target_date = date.today()
        
        if old_identity == new_identity:
            return
        
        pipeline = self.redis_client.pipeline()
        
        # 生成时间字符串
        day_str = self._get_time_string(target_date, 'day')
        month_str = self._get_time_string(target_date, 'month')
        year_str = self._get_time_string(target_date, 'year')
        
        periods = ['day', 'month', 'year']
        time_strings = [day_str, month_str, year_str]
        
        # 从旧分榜获取用户当前分数
        old_scores = {}
        for period, time_str in zip(periods, time_strings):
            old_key = self._get_rank_key(period, old_identity, time_str)
            score = self.redis_client.zscore(old_key, str(user_id))
            if score is not None:
                old_scores[period] = int(score)
                # 从旧分榜移除
                pipeline.zrem(old_key, str(user_id))
        
        # 添加到新分榜
        for period, time_str in zip(periods, time_strings):
            if period in old_scores:
                new_key = self._get_rank_key(period, new_identity, time_str)
                pipeline.zadd(new_key, {str(user_id): old_scores[period]})
        
        pipeline.execute()


# 创建全局实例
ranking_service = RankingService()
