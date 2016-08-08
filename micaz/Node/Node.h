#ifndef NODE_H
#define NODE_H

enum {
    NREADINGS = 10,
    DEFAULT_INTERVAL = 200,
    AM_NODEREAD = 0x8A,
    QUEUESIZE = 10,
    PHOTO = 1,
    TEMP = 2,
};

typedef nx_struct readings {
	nx_uint16_t version;
    nx_uint8_t filler;
	nx_uint8_t ttl;
    nx_uint8_t type;
	nx_uint16_t id;
	nx_uint8_t count;
	nx_uint16_t readings[NREADINGS];
} readings_t;

#endif
