// Exporto o mesmo núcleo do firmware para conferir todos os escores no Windows.
#include "../main/har_inference.h"
__declspec(dllexport) int predict(const int8_t *x, int32_t *scores) {
    return har_predict(x, scores);
}
