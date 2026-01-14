#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"

extern int asm_compute(void);

int main(void) {
    stdio_init_all();

    if (cyw43_arch_init()) {
        while (true) { tight_loop_contents(); }
    }

    int result = asm_compute();

    int delay_ms = result * 1000;
    if (delay_ms < 50) delay_ms = 50;

    while (true) {
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 1);
        sleep_ms(delay_ms);
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 0);
        sleep_ms(delay_ms);
    }
}

