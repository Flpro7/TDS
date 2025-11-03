"""Economy utilities for tracking player resources."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PlayerStats:
    """Lightweight container for player economy information."""

    money: int
    lives: int
    current_wave: int = 0

    def gain_money(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Amount must be positive")
        self.money += amount

    def can_afford(self, cost: int) -> bool:
        return cost <= self.money

    def spend_money(self, cost: int) -> bool:
        if cost < 0:
            raise ValueError("Cost must be positive")
        if cost > self.money:
            return False
        self.money -= cost
        return True

    def lose_life(self, amount: int = 1) -> None:
        if amount < 0:
            raise ValueError("Amount must be positive")
        self.lives = max(0, self.lives - amount)

    def is_alive(self) -> bool:
        return self.lives > 0

    def register_enemy_kill(self, reward: int) -> None:
        self.gain_money(reward)

    def register_purchase(self, cost: int) -> bool:
        return self.spend_money(cost)

    def start_wave(self, wave_number: int) -> None:
        self.current_wave = wave_number
