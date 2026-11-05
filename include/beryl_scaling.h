#ifndef GUARD_BERYL_SCALING_H
#define GUARD_BERYL_SCALING_H

// Gym leaders in Beryl can be fought in any order, so their teams follow the
// player's badge count (docs/beryl/GAME_PLAN.md, "Levels").
#define BERYL_LEVEL_ANCHOR 50

u32 Beryl_BadgeCount(void);
u32 Beryl_GymLevel(void);
void Beryl_ScaleTrainerParty(struct Pokemon *party, u16 trainerNum);

#endif // GUARD_BERYL_SCALING_H
