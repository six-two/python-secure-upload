import logging
import time
from typing import Optional

logger = logging.getLogger("IP blocks")
logger.setLevel(logging.DEBUG)
c_handler = logging.StreamHandler()
c_format = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)


class IpAddressBlocker:
    def __init__(self, allowed_ips: list[str], denied_ips: list[str], block_threshold: int, block_duration: int) -> None:
        """
        Creates an IP address blocker.
        If an IP address is both in allowed_ips and denied_ips, the entry in denied_ips will take precedence.
        If an IP is in neither, failed authentication attempts will be tracked.
        After `block_threshold` fails are recorded, the address will be blocked.
        `block_duration` seconds after the first block, all temporary blocks will be reset.
        """
        self.allowed_ips = set(allowed_ips)
        self.denied_ips = set(denied_ips)
        # Start: Variables for temporary blocks
        # Set of IP addresses that have exceeded the threshold
        self.block_ip_set = set()
        # Counts of failed attempts for addressed below the threshld
        self.block_counts_map: dict[str, int] = {}
        # None means no blocks are currently active
        # As soon as a block is made, the time is stored. This prevents some blocks from expiring prematurely
        self.block_period_start: Optional[float] = None
        self.block_threshold = block_threshold
        self.block_duration = block_duration
        # End: Variables for temporary blocks

    def update_blocks(self) -> None:
        """
        We could store each failed attempt with a timestamp and track it accurately,
        but it would be way easier to implement (and thus less error prone) to just reset all blocks periodically
        """
        now = time.monotonic()
        if self.block_period_start and now > self.block_period_start + self.block_duration:
            # Block period expired, reset all blocks
            self.block_ip_set = set()
            self.block_counts_map = {}
            self.block_period_start = None
            logger.info("Reset temporary blocks")

    def increase_failed_auth_count(self, ip_address: str) -> None:
        if ip_address in self.block_ip_set:
            # already blocked
            return
        elif ip_address in self.allowed_ips or ip_address in self.denied_ips:
            # already have an existing rule for this ip
            return
        else:
            # Start the timer if this is the first block
            if not self.block_period_start:
                now = time.monotonic()
                self.block_period_start = now
                logger.debug("Blocking period timer started")

            try:
                # Increase existing fail count by one
                self.block_counts_map[ip_address] += 1
            except KeyError:
                # No entry for ip address, so we start a new count for it
                self.block_counts_map[ip_address] = 1
            
            logger.debug(f"{ip_address} has {self.block_counts_map[ip_address]} failed authentication attempt(s)")
            # This needs to be here in case block_threshold is set to one
            if self.block_counts_map[ip_address] >= self.block_threshold:
                # Threshold exceeded -> put on block list, remove counter
                self.block_ip_set.add(ip_address)
                del self.block_counts_map[ip_address]
                logger.info(f"Temporarily blocked {ip_address}")

    def is_blocked(self, ip_address: str) -> bool:
        if ip_address in self.denied_ips:
            # Process deny entries first, since they have the highest priority
            return True
        elif ip_address in self.allowed_ips:
            # Permanently allowed
            return False
        else:
            # No static rule, so we check the temporary block list
            return ip_address in self.block_ip_set
