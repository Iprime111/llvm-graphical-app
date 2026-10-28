#include "sim.h"

#define SCENE_X 768
#define PLANET_Y 515
#define PLANET_RADIUS 180
#define ATMOSPHERE_RADIUS 185
#define PLANET_SHADOW_EDGE -35
#define PLANET_ICE_EDGE -150

#define WEST_LAND_X -65
#define WEST_LAND_Y 15
#define WEST_LAND_SIZE 16000
#define EAST_LAND_X 80
#define EAST_LAND_Y -65
#define EAST_LAND_SIZE 13000
#define LAND_STRETCH 2

#define SHIP_STERN_X 505
#define SHIP_HULL_LEFT 540
#define SHIP_HULL_RIGHT 1000
#define SHIP_HULL_TOP 111
#define SHIP_HULL_BOTTOM 201
#define SHIP_PROW_X 1090
#define SHIP_PROW_MID_Y 156
#define SHIP_TRIM_WIDTH 3
#define SHIP_ENGINE_X 480
#define SHIP_ENGINE_WIDTH 25
#define SHIP_ENGINE_TOP 127
#define SHIP_ENGINE_BOTTOM 189
#define SHIP_TOWER_LEFT 590
#define SHIP_TOWER_RIGHT 720
#define SHIP_TOWER_BASE_Y 111
#define SHIP_MAIN_TOWER_X 610
#define SHIP_MAIN_TOWER_RIGHT 654
#define SHIP_MAIN_TOWER_TOP 49
#define SHIP_MAIN_SPIRE_X 627
#define SHIP_MAIN_SPIRE_TOP 8
#define SHIP_SIDE_TOWER_X 668
#define SHIP_SIDE_TOWER_RIGHT 702
#define SHIP_SIDE_TOWER_TOP 67
#define SHIP_SIDE_SPIRE_X 681
#define SHIP_SIDE_SPIRE_TOP 24
#define SHIP_TOWER_DECK_TOP 83
#define SHIP_TOWER_WINDOW_TOP 77
#define SHIP_GUN_START 595
#define SHIP_GUN_END 980
#define SHIP_GUN_GAP 56
#define SHIP_GUN_TOP 139
#define SHIP_GUN_BOTTOM 160
#define SHIP_GUN_BAY_WIDTH 35
#define SHIP_GUN_WINDOW_WIDTH 10
#define SHIP_LOWER_DECK_Y 172
#define SHIP_HANGAR_LEFT 625
#define SHIP_HANGAR_RIGHT 870
#define SHIP_HANGAR_BOTTOM 219
#define SHIP_LANCE_LEFT 755
#define SHIP_LANCE_RIGHT 781
#define SHIP_CANNON_LENGTH 27
#define SHIP_NOZZLE_Y 241

#define STAR_COUNT 190
#define STAR_START_X 73
#define STAR_START_Y 31
#define STAR_STEP_X 347
#define STAR_STEP_Y 197
#define BRIGHT_STAR_GAP 9

#define CHARGE_FRAME 6
#define BEAM_FRAME 10
#define BLAST_FRAME 20
#define IMPACT_END_FRAME 28
#define SMOKE_FRAME 38
#define SMOKE_END_FRAME 52
#define FRAME_COUNT 56
#define CHARGE_RADIUS 3
#define CHARGE_GROWTH 3
#define BEAM_GROWTH 10
#define BEAM_REACH_Y 350
#define BEAM_HALO_HALF 13
#define BEAM_BODY_HALF 7
#define BEAM_CORE_HALF 2
#define IMPACT_RADIUS 7
#define IMPACT_GROWTH 5
#define FIREBALL_GROWTH 14
#define SMOKE_RADIUS 245
#define SMOKE_SHRINK 13
#define SMOKE_DARK_STEP 7

#define SPACE_COLOR 0xff030712
#define STAR_COLOR 0xff668299
#define BRIGHT_STAR_COLOR 0xffb9d3df
#define ATMOSPHERE_COLOR 0xff1a5167
#define OCEAN_NIGHT_COLOR 0xff071b2a
#define LAND_NIGHT_COLOR 0xff183027
#define OCEAN_DAY_COLOR 0xff123b52
#define LAND_DAY_COLOR 0xff315642
#define ICE_COLOR 0xff607d83
#define HULL_COLOR 0xff303b45
#define HULL_LIGHT_COLOR 0xff56616a
#define HULL_DARK_COLOR 0xff1b252f
#define GOLD_COLOR 0xff9f8152
#define GOLD_LIGHT_COLOR 0xffc2a16a
#define GUN_COLOR 0xff252d35
#define WINDOW_COLOR 0xffa22f2b
#define ENGINE_COLOR 0xff46a4b7
#define CHARGE_COLOR 0xffffd98a
#define BEAM_HALO_COLOR 0xff6e247e
#define BEAM_BODY_COLOR 0xffff5366
#define BEAM_CORE_COLOR 0xfffff1bd
#define IMPACT_COLOR 0xffffdd83
#define FIRE_OUTER_COLOR 0xff9c2529
#define FIRE_ORANGE_COLOR 0xffed6326
#define FIRE_YELLOW_COLOR 0xffffb840
#define FIRE_CORE_COLOR 0xffffebaa
#define SMOKE_RED_COLOR 0xff3c1720
#define SMOKE_DARK_COLOR 0xff190d17

#define APP_NOINLINE __attribute__((noinline))

// Noinline attribute is placed to share box() between other functions
// Otherwise, IR becomes 150-200 lines longer
APP_NOINLINE static void box(int left, int top, int right, int bottom, int color)
{
    for (int y = top; y < bottom; y++) {
        for (int x = left; x < right; x++) {
            simPutPixel(x, y, color);
        }
    }
}

static void disk(int center_x, int center_y, int radius, int color)
{
    for (int y = center_y - radius; y <= center_y + radius; y++) {
        for (int x = center_x - radius; x <= center_x + radius; x++) {
            int dx = x - center_x;
            int dy = y - center_y;
            if (x >= 0 && x < SIM_X_SIZE && y >= 0 && y < SIM_Y_SIZE &&
                dx * dx + dy * dy <= radius * radius) {
                simPutPixel(x, y, color);
            }
        }
    }
}

static void background(void)
{
    int x = STAR_START_X;
    int y = STAR_START_Y;
    int bright = 0;

    box(0, 0, SIM_X_SIZE, SIM_Y_SIZE, SPACE_COLOR);
    for (int i = 0; i < STAR_COUNT; i++) {
        x += STAR_STEP_X;
        y += STAR_STEP_Y;
        if (x >= SIM_X_SIZE) {
            x -= SIM_X_SIZE;
        }
        if (y >= SIM_Y_SIZE) {
            y -= SIM_Y_SIZE;
        }
        simPutPixel(x, y, STAR_COLOR);
        bright++;
        if (bright == BRIGHT_STAR_GAP) {
            if (x + 1 < SIM_X_SIZE) {
                simPutPixel(x + 1, y, BRIGHT_STAR_COLOR);
            }
            bright = 0;
        }
    }
}

static void planet(void)
{
    for (int y = PLANET_Y - ATMOSPHERE_RADIUS;
         y <= PLANET_Y + ATMOSPHERE_RADIUS; y++) {
        int dy = y - PLANET_Y;
        for (int x = SCENE_X - ATMOSPHERE_RADIUS;
             x <= SCENE_X + ATMOSPHERE_RADIUS; x++) {
            int dx = x - SCENE_X;
            int distance = dx * dx + dy * dy;
            int west_x = dx - WEST_LAND_X;
            int west_y = dy - WEST_LAND_Y;
            int east_x = dx - EAST_LAND_X;
            int east_y = dy - EAST_LAND_Y;
            int land = west_x * west_x + LAND_STRETCH * west_y * west_y < WEST_LAND_SIZE ||
                       LAND_STRETCH * east_x * east_x + east_y * east_y < EAST_LAND_SIZE;
            int color = ATMOSPHERE_COLOR;

            if (distance > ATMOSPHERE_RADIUS * ATMOSPHERE_RADIUS) {
                continue;
            }
            if (distance <= PLANET_RADIUS * PLANET_RADIUS) {
                if (dx < PLANET_SHADOW_EDGE) {
                    color = OCEAN_NIGHT_COLOR;
                    if (land) {
                        color = LAND_NIGHT_COLOR;
                    }
                } else {
                    color = OCEAN_DAY_COLOR;
                    if (land) {
                        color = LAND_DAY_COLOR;
                    }
                }
                if (dy < PLANET_ICE_EDGE) {
                    color = ICE_COLOR;
                }
            }
            simPutPixel(x, y, color);
        }
    }
}

static void ship(void)
{
    // Ship's hull
    for (int y = SHIP_HULL_TOP; y <= SHIP_HULL_BOTTOM; y++) {
        int reach = y - SHIP_HULL_TOP;
        if (y > SHIP_PROW_MID_Y) {
            reach = SHIP_HULL_BOTTOM - y;
        }
        int nose = SHIP_HULL_RIGHT + reach * 2;
        box(SHIP_HULL_LEFT, y, nose + 1, y + 1, HULL_COLOR);
        simPutPixel(nose, y, GOLD_COLOR);
    }
    box(SHIP_HULL_LEFT, SHIP_HULL_TOP, SHIP_HULL_RIGHT,
        SHIP_HULL_TOP + SHIP_TRIM_WIDTH, GOLD_COLOR);
    box(SHIP_HULL_LEFT, SHIP_GUN_BOTTOM, SHIP_HULL_RIGHT,
        SHIP_GUN_BOTTOM + SHIP_TRIM_WIDTH, GOLD_COLOR);
    box(SHIP_HULL_LEFT, SHIP_LOWER_DECK_Y, SHIP_HULL_RIGHT,
        SHIP_LOWER_DECK_Y + SHIP_TRIM_WIDTH, HULL_LIGHT_COLOR);

    // Engines and cathedral towers
    box(SHIP_STERN_X, SHIP_HULL_TOP, SHIP_HULL_LEFT,
        SHIP_HULL_BOTTOM, HULL_DARK_COLOR);
    box(SHIP_ENGINE_X, SHIP_ENGINE_TOP,
        SHIP_ENGINE_X + SHIP_ENGINE_WIDTH, SHIP_ENGINE_BOTTOM, ENGINE_COLOR);
    box(SHIP_TOWER_LEFT, SHIP_TOWER_DECK_TOP,
        SHIP_TOWER_RIGHT, SHIP_TOWER_BASE_Y, HULL_DARK_COLOR);
    box(SHIP_MAIN_TOWER_X, SHIP_MAIN_TOWER_TOP,
        SHIP_MAIN_TOWER_RIGHT, SHIP_TOWER_BASE_Y, HULL_LIGHT_COLOR);
    box(SHIP_MAIN_SPIRE_X, SHIP_MAIN_SPIRE_TOP,
        SHIP_MAIN_SPIRE_X + SHIP_GUN_WINDOW_WIDTH,
        SHIP_MAIN_TOWER_TOP, GOLD_LIGHT_COLOR);
    box(SHIP_SIDE_TOWER_X, SHIP_SIDE_TOWER_TOP,
        SHIP_SIDE_TOWER_RIGHT, SHIP_TOWER_BASE_Y, HULL_LIGHT_COLOR);
    box(SHIP_SIDE_SPIRE_X, SHIP_SIDE_SPIRE_TOP,
        SHIP_SIDE_SPIRE_X + SHIP_TRIM_WIDTH * 2,
        SHIP_SIDE_TOWER_TOP, GOLD_LIGHT_COLOR);
    box(SHIP_MAIN_TOWER_X + SHIP_TRIM_WIDTH, SHIP_TOWER_WINDOW_TOP,
        SHIP_MAIN_TOWER_X + SHIP_GUN_WINDOW_WIDTH + SHIP_TRIM_WIDTH,
        SHIP_TOWER_DECK_TOP + SHIP_GUN_WINDOW_WIDTH, WINDOW_COLOR);
    box(SHIP_SIDE_TOWER_X + SHIP_GUN_WINDOW_WIDTH, SHIP_TOWER_DECK_TOP,
        SHIP_SIDE_TOWER_X + SHIP_GUN_WINDOW_WIDTH * 2,
        SHIP_TOWER_BASE_Y - SHIP_TRIM_WIDTH, WINDOW_COLOR);

    // Guns
    for (int x = SHIP_GUN_START; x < SHIP_GUN_END; x += SHIP_GUN_GAP) {
        box(x, SHIP_GUN_TOP, x + SHIP_GUN_BAY_WIDTH,
            SHIP_GUN_BOTTOM, GUN_COLOR);
        box(x + SHIP_TRIM_WIDTH, SHIP_GUN_TOP + SHIP_TRIM_WIDTH,
            x + SHIP_TRIM_WIDTH + SHIP_GUN_WINDOW_WIDTH,
            SHIP_GUN_BOTTOM - SHIP_TRIM_WIDTH, WINDOW_COLOR);
    }

    // Lance
    box(SHIP_HANGAR_LEFT, SHIP_HULL_BOTTOM,
        SHIP_HANGAR_RIGHT, SHIP_HANGAR_BOTTOM, HULL_DARK_COLOR);
    box(SHIP_LANCE_LEFT, SHIP_HANGAR_BOTTOM,
        SHIP_LANCE_RIGHT, SHIP_NOZZLE_Y, HULL_LIGHT_COLOR);
    box(SHIP_LANCE_LEFT + SHIP_TRIM_WIDTH,
        SHIP_NOZZLE_Y - SHIP_TRIM_WIDTH,
        SHIP_LANCE_RIGHT - SHIP_TRIM_WIDTH,
        SHIP_NOZZLE_Y + SHIP_TRIM_WIDTH, WINDOW_COLOR);
    box(SHIP_PROW_X, SHIP_PROW_MID_Y,
        SHIP_PROW_X + SHIP_CANNON_LENGTH,
        SHIP_PROW_MID_Y + SHIP_TRIM_WIDTH, GUN_COLOR);
}

static void beam(int end_y)
{
    for (int y = SHIP_NOZZLE_Y; y <= end_y; y++) {
        for (int x = SCENE_X - BEAM_HALO_HALF;
             x <= SCENE_X + BEAM_HALO_HALF; x++) {
            int color = BEAM_HALO_COLOR;
            if (x >= SCENE_X - BEAM_BODY_HALF &&
                x <= SCENE_X + BEAM_BODY_HALF) {
                color = BEAM_BODY_COLOR;
            }
            if (x >= SCENE_X - BEAM_CORE_HALF &&
                x <= SCENE_X + BEAM_CORE_HALF) {
                color = BEAM_CORE_COLOR;
            }
            simPutPixel(x, y, color);
        }
    }
}

static void fireball(int radius)
{
    disk(SCENE_X, PLANET_Y, radius, FIRE_OUTER_COLOR);
    disk(SCENE_X, PLANET_Y, radius * 3 / 4, FIRE_ORANGE_COLOR);
    disk(SCENE_X, PLANET_Y, radius / 2, FIRE_YELLOW_COLOR);
    disk(SCENE_X, PLANET_Y, radius / 4, FIRE_CORE_COLOR);
}

void app(void)
{
    for (int frame = 0; frame < FRAME_COUNT; frame++) {
        background();
        if (frame < SMOKE_FRAME) {
            planet();
        }
        ship();

        if (frame >= CHARGE_FRAME && frame < BEAM_FRAME) {
            disk(SCENE_X, SHIP_NOZZLE_Y,
                 CHARGE_RADIUS + (frame - CHARGE_FRAME) * CHARGE_GROWTH,
                 CHARGE_COLOR);
        }
        if (frame >= BEAM_FRAME && frame < BLAST_FRAME) {
            beam(SHIP_NOZZLE_Y + (frame - BEAM_FRAME + 1) * BEAM_GROWTH);
        }
        if (frame >= BLAST_FRAME && frame < SMOKE_FRAME) {
            if (frame < IMPACT_END_FRAME) {
                beam(BEAM_REACH_Y);
                disk(SCENE_X, PLANET_Y - PLANET_RADIUS,
                     IMPACT_RADIUS + (frame - BLAST_FRAME) * IMPACT_GROWTH,
                     IMPACT_COLOR);
            }
            fireball((frame - BLAST_FRAME + 1) * FIREBALL_GROWTH);
        }
        if (frame >= SMOKE_FRAME && frame < SMOKE_END_FRAME) {
            int step = frame - SMOKE_FRAME + 1;
            int color = SMOKE_RED_COLOR;
            if (step >= SMOKE_DARK_STEP) {
                color = SMOKE_DARK_COLOR;
            }
            disk(SCENE_X, PLANET_Y, SMOKE_RADIUS - step * SMOKE_SHRINK, color);
        }
        simFlush();
    }
}
