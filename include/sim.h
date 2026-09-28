#ifndef SIM_H
#define SIM_H

#define SIM_X_SIZE 1536//512
#define SIM_Y_SIZE 768//256

#ifndef __sim__
void simInit(void);
void app(void);
void simExit(void);
void simFlush(void);
void simPutPixel(int x, int y, int argb);
int simRand(void);
int simHasClick(void);
int simGetClick(void);
#endif // __sim__

#endif // SIM_H
