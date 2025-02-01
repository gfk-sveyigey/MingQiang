import time
import threading

class SnowflakeIDGenerator:
    def __init__(self, machine_id, datacenter_id, epoch=1609459200000):
        """
        初始化雪花 ID 生成器

        :param machine_id: 机器 ID
        :param datacenter_id: 数据中心 ID
        :param epoch: 雪花算法的起始时间（时间戳）
        """
        self.machine_id = machine_id
        self.datacenter_id = datacenter_id
        self.epoch = epoch  # 自定义一个起始时间，通常是某个固定时间点

        # 位移配置
        self.timestamp_bits = 41  # 时间戳占位
        self.datacenter_bits = 5  # 数据中心 ID 位数
        self.machine_bits = 5  # 机器 ID 位数
        self.sequence_bits = 12  # 序列号位数

        # 计算最大值
        self.max_datacenter_id = -1 ^ (-1 << self.datacenter_bits)
        self.max_machine_id = -1 ^ (-1 << self.machine_bits)
        self.max_sequence = -1 ^ (-1 << self.sequence_bits)

        # 位移量
        self.timestamp_shift = self.sequence_bits + self.machine_bits + self.datacenter_bits
        self.datacenter_shift = self.sequence_bits + self.machine_bits
        self.machine_shift = self.sequence_bits

        # 上次生成 ID 的时间戳
        self.last_timestamp = -1
        self.sequence = 0
        self.lock = threading.Lock()

    def _current_timestamp(self):
        """返回当前时间戳（毫秒）"""
        return int(time.time() * 1000)  # 毫秒

    def _wait_for_next_timestamp(self, last_timestamp):
        """等待下一个毫秒"""
        timestamp = self._current_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._current_timestamp()
        return timestamp

    def generate(self):
        """生成雪花 ID"""
        with self.lock:
            timestamp = self._current_timestamp()

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.max_sequence
                if self.sequence == 0:
                    timestamp = self._wait_for_next_timestamp(self.last_timestamp)
            else:
                self.sequence = 0

            if timestamp < self.last_timestamp:
                raise Exception("Clock moved backwards, refusing to generate ID")

            self.last_timestamp = timestamp

            # 生成雪花 ID
            snowflake_id = ((timestamp - self.epoch) << self.timestamp_shift) | \
                           (self.datacenter_id << self.datacenter_shift) | \
                           (self.machine_id << self.machine_shift) | \
                           self.sequence

            return snowflake_id

house_id_generator = SnowflakeIDGenerator(333, 111)
user_id_generator = SnowflakeIDGenerator(333, 333)
