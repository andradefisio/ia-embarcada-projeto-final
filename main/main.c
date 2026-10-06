#include <stdio.h>
#include <inttypes.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_system.h"
#include "har_inference.h"
#include "generated/test_data.h"

#define BUTTON_DEMO GPIO_NUM_4
#define BUTTON_TEST GPIO_NUM_5
#define LED_OK GPIO_NUM_6
#define LED_ERROR GPIO_NUM_7

static void run_test(int full) {
    const int total = full ? HAR_TEST_COUNT : HAR_DEMO_COUNT;
    int correct = 0;
    int confusion[HAR_CLASSES][HAR_CLASSES] = {0};
    int64_t inference_us = 0;
    printf("\n=== %s: %d janelas ===\n", full ? "TESTE COMPLETO" : "DEMONSTRACAO", total);
    for (int n = 0; n < total; ++n) {
        const int index = full ? n : HAR_DEMO_INDEX[n];
        int32_t scores[HAR_CLASSES];
        const int64_t start = esp_timer_get_time();
        // Os dados estão em flash. Aqui calculo a previsão no ESP32;
        // só depois consulto o rótulo para avaliar se houve acerto.
        const int prediction = har_predict(HAR_TEST_X[index], scores);
        inference_us += esp_timer_get_time() - start;
        const int truth = HAR_TEST_Y[index];
        const int ok = prediction == truth;
        correct += ok;
        confusion[truth][prediction]++;
        gpio_set_level(LED_OK, ok);
        gpio_set_level(LED_ERROR, !ok);
        if (!full) {
            printf("%02d/%d | linha=%d | real=%s | previsto=%s | %s\n",
                   n+1, total, index+1, HAR_LABELS[truth], HAR_LABELS[prediction], ok ? "ACERTO" : "ERRO");
            vTaskDelay(pdMS_TO_TICKS(1800));
        } else if ((n+1) % 250 == 0) {
            printf("Progresso: %d/%d\n", n+1, total);
        }
        if (full && n % 32 == 0) vTaskDelay(1);
    }
    printf("RESULTADO: %d/%d acertos | acuracia=%.4f%% | media de inferencia=%" PRId64 " us\n",
           correct, total, 100.0 * correct / total, inference_us / total);
    printf("Matriz de confusao: linhas=real; colunas=previsto; ordem das classes 1 a 6\n");
    for (int c = 0; c < HAR_CLASSES; ++c) {
        for (int p = 0; p < HAR_CLASSES; ++p) printf("%5d", confusion[c][p]);
        printf("\n");
    }
    printf("Heap livre: %lu bytes. Botao DEMO repete; TESTE avalia as 2947 janelas.\n",
           (unsigned long)esp_get_free_heap_size());
}

void app_main(void) {
    gpio_config_t buttons = {.pin_bit_mask = (1ULL << BUTTON_DEMO) | (1ULL << BUTTON_TEST),
        .mode = GPIO_MODE_INPUT, .pull_up_en = GPIO_PULLUP_ENABLE};
    gpio_config_t leds = {.pin_bit_mask = (1ULL << LED_OK) | (1ULL << LED_ERROR), .mode = GPIO_MODE_OUTPUT};
    gpio_config(&buttons);
    gpio_config(&leds);
    printf("\nMeu projeto: reconhecimento de atividades humanas no ESP32-S3\n");
    printf("561 entradas int8 -> 6 classes | pesos+bias: %u bytes\n",
           (unsigned)(sizeof(HAR_WEIGHTS) + sizeof(HAR_BIAS)));
    printf("Replay das features UCI; nao e captura de sensor ao vivo.\n");
    for (int c = 0; c < HAR_CLASSES; ++c) printf("Classe %d: %s\n", c+1, HAR_LABELS[c]);
    run_test(0);
    while (1) {
        int demo = !gpio_get_level(BUTTON_DEMO);
        int full = !gpio_get_level(BUTTON_TEST);
        if (demo || full) {
            vTaskDelay(pdMS_TO_TICKS(40));
            if (!gpio_get_level(demo ? BUTTON_DEMO : BUTTON_TEST)) run_test(full);
            while (!gpio_get_level(BUTTON_DEMO) || !gpio_get_level(BUTTON_TEST)) vTaskDelay(pdMS_TO_TICKS(20));
        }
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
