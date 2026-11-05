#include "global.h"
#include "event_data.h"
#include "pokemon.h"
#include "beryl_scaling.h"
#include "constants/items.h"
#include "constants/opponents.h"

// Leaders whose teams scale. Their party in trainers.party is written as if the
// ace were level BERYL_LEVEL_ANCHOR; the others are listed relative to that.
// The last Pokémon of each party is the ace and is always brought.
static const u16 sScaledLeaders[] =
{
    TRAINER_ROXANNE_1,       // ISOLDE, Frostspring (Ice)
    TRAINER_BRAWLY_1,        // BRANNOCK, Cragmoor (Rock)
    TRAINER_WATTSON_1,       // MAREN, Pinehollow (Dragon)
    TRAINER_FLANNERY_1,      // NERISSA, Weirhaven (Water)
    TRAINER_NORMAN_1,        // ODA, Lanterncross (Ghost)
    TRAINER_WINONA_1,        // CASSIAN, Valecrown (Electric)
    TRAINER_TATE_AND_LIZA_1, // SEDGE, Reedmouth (Grass)
    TRAINER_JUAN_1,          // TORVALD, Stillbrook (Fighting)
};

u32 Beryl_BadgeCount(void)
{
    u32 i, n = 0;
    for (i = FLAG_BADGE01_GET; i <= FLAG_BADGE08_GET; i++)
    {
        if (FlagGet(i))
            n++;
    }
    return n;
}

// The level of the next gym leader's ace: 12 with no badges, +6 per badge.
u32 Beryl_GymLevel(void)
{
    return 12 + 6 * Beryl_BadgeCount();
}

static bool32 IsScaledLeader(u16 trainerNum)
{
    u32 i;
    for (i = 0; i < ARRAY_COUNT(sScaledLeaders); i++)
    {
        if (sScaledLeaders[i] == trainerNum)
            return TRUE;
    }
    return FALSE;
}

static void SetMonLevel(struct Pokemon *mon, u32 level)
{
    u32 i;
    enum Species species;

    SetMonData(mon, MON_DATA_LEVEL, &level);
    // Evolve into the form a trainer's Pokémon would have reached by this level.
    for (i = 0; i < 3; i++)
    {
        enum Species target = GetEvolutionTargetSpecies(mon, EVO_MODE_NORMAL, ITEM_NONE, NULL, NULL, CHECK_EVO);
        if (target == SPECIES_NONE)
            break;
        SetMonData(mon, MON_DATA_SPECIES, &target);
    }
    species = GetMonData(mon, MON_DATA_SPECIES);
    SetMonData(mon, MON_DATA_EXP, &gExperienceTables[gSpeciesInfo[species].growthRate][level]);
    CalculateMonStats(mon);
    GiveMonInitialMoveset(mon);
    {
        u32 hp = GetMonData(mon, MON_DATA_MAX_HP);
        SetMonData(mon, MON_DATA_HP, &hp);
    }
}

void Beryl_ScaleTrainerParty(struct Pokemon *party, u16 trainerNum)
{
    u32 i, count = 0, keep, badges, gym;

    if (!IsScaledLeader(trainerNum))
        return;

    while (count < PARTY_SIZE && GetMonData(&party[count], MON_DATA_SPECIES) != SPECIES_NONE)
        count++;
    if (count == 0)
        return;

    badges = Beryl_BadgeCount();
    gym = Beryl_GymLevel();

    // Leaders bring 2 + badges/2 Pokémon: the first ones in their list, plus their ace.
    keep = 2 + badges / 2;
    if (keep < count)
    {
        party[keep - 1] = party[count - 1];
        for (i = keep; i < count; i++)
            ZeroMonData(&party[i]);
        count = keep;
    }

    for (i = 0; i < count; i++)
    {
        s32 level = (s32)GetMonData(&party[i], MON_DATA_LEVEL) - BERYL_LEVEL_ANCHOR + (s32)gym;
        if (level < 2)
            level = 2;
        if (level > MAX_LEVEL)
            level = MAX_LEVEL;
        SetMonLevel(&party[i], level);
    }
}
