from ...Resources import EStatus, ECondition

__all__ = (
    'Status'
    )

class Status:

    __slots__ = (
        '_conditions',
        '_attack_conditions',
        '_targeting_conditions',
        '_taking_damage_conditions',
        '_add_status'
    )

    def __init__(self):
        self._conditions: list[ECondition] = []

        self._attack_conditions: dict[EStatus, int] = {}
        # Adding the same Attacking conditions increase the number of turns in which Status reamins active

        self._targeting_conditions: list[EStatus] = []
        # Adding the same Targeting conditions does nothing

        self._taking_damage_conditions = []
        # Cannot directly add Taking Damage Condition, only from OverTimeDamage
        # Taking Damage Conditions persist within the duration of Over Time Damages

        self._add_status = self._add_condition


    def _add_condition(self, condition: ECondition, status: EStatus, turns: int = 0) -> None:
        match condition:
            case ECondition.Attacking:
                if status in self._attack_conditions:
                    self._attack_conditions[status] += turns
                else:
                    self._attack_conditions[status] = turns

            case ECondition.TakeDamage:
                if status not in self._taking_damage_conditions:
                    self._taking_damage_conditions.append(status)
            
            case ECondition.Targeting:
                if status not in self._targeting_conditions:
                    self._targeting_conditions.append(status)

        if condition not in self._conditions:
            self._conditions.append(condition)

    def _check_status(self, status: EStatus) -> bool:
        return (
            status in self._targeting_conditions or 
            status in self._taking_damage_conditions or
            status in self._attack_conditions
        )

    def _check_condition(self, condition: ECondition) -> bool:
        return condition in self._conditions

    def _end_turn(self):
        for status, turns in self._attack_conditions.items():
            turns -= 1
            if turns == 0:
                self._remove_status(status)
        
        for status in self._targeting_conditions:
            self._remove_status(status)

    def _remove_status(self, status: EStatus) -> None:
        if status in self._attack_conditions:
            del self._attack_conditions[status]
            if self._attack_conditions.__len__() == 0:
                self._conditions.remove(ECondition.Attacking)
        elif status in self._targeting_conditions:
            self._targeting_conditions.remove(status)
            if self._targeting_conditions.__len__() == 0:
                self._conditions.remove(ECondition.Targeting)
        elif status in self._taking_damage_conditions:
            self._taking_damage_conditions.remove(status)
            if self._taking_damage_conditions.__len__() == 0:
                self._conditions.remove(ECondition.TakeDamage)
