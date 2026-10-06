#pragma once
#include "generated/model_data.h"

// Treinei uma regressão logística multiclasse. Para escolher a classe,
// basta comparar os escores: a softmax não muda a ordem e seria um custo extra.
// O mesmo núcleo é usado no firmware e na verificação no computador.
static inline int har_predict(const int8_t *x, int32_t scores[HAR_CLASSES]) {
    int best = 0;
    for (int c = 0; c < HAR_CLASSES; ++c) {
        int32_t acc = HAR_BIAS[c];
        for (int j = 0; j < HAR_FEATURES; ++j) {
            acc += (int32_t)x[j] * (int32_t)HAR_WEIGHTS[c][j];
        }
        scores[c] = acc;
        if (c > 0 && acc > scores[best]) best = c;
    }
    return best;
}
