#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <malloc.h>

#define MAX_LISTING_COUNT   0x10
#define MAX_LISTING_SIZE    0x1000

class ListingContent {
public:
    int price;
    size_t name_size;
    char* name;

    ListingContent(size_t n) {
        if (n <= 0) {
            printf("nt\n");
            exit(1);
        }

        name_size = n;

        name = (char*)malloc(name_size);
    }
    ~ListingContent() {
        if(name != 0) {
            free(name);
            name = 0;
        }
    }

    virtual void ShowListing() {
        (*(void(**)(char*))name)(&name[8]);
    }
};

class ExtendedListingContent : public ListingContent {
public:
    using ListingContent::ListingContent;

    void ShowListing() {
        printf("Content: %s\n", name);
        printf("Price: %d\n", price);
    }
};

void menu() {
    printf("1. Create new listing\n");
    printf("2. Edit listing\n");
    printf("3. Delete listing\n");
    printf("4. Inspect listing\n");
    printf("5. Exit\n");
    printf("> ");
}


size_t get_index() {
    printf("Index: ");
    size_t index;
    scanf("%zu", &index);

    if (index > (MAX_LISTING_COUNT-1)) {
        printf("Index out of range!\n");
        exit(1);
    }

    return index;
}

size_t get_size() {
    printf("Size: ");
    size_t size;
    scanf("%zu", &size);

    return size;
}

struct Listing {
    ExtendedListingContent* listing;
    bool in_use;
};

Listing listings[MAX_LISTING_COUNT];

int main() {
    size_t index;
    size_t listing_size;
    size_t choice;
    int cnt;

    setbuf(stdin, NULL);
    setbuf(stdout, NULL);
    setbuf(stderr, NULL);

    printf("Welcome to Alfred's marketplace!\n");

    while(1) {
        menu();
        scanf("%zu", &choice);
        
        switch(choice) {
            case 1:
                index = get_index();
                if(listings[index].in_use) {
                    printf("This slot is already in use!\n");
                    break;
                }

                listing_size = get_size();

                if (listing_size > MAX_LISTING_SIZE) {
                    printf("Listing too big!\n");
                    break;
                }

                listings[index].listing = new ExtendedListingContent(listing_size);
                listings[index].in_use = true;
                printf("Created listing at index %zu!\n", index);
                break;
            case 2:
                index = get_index();
                if (!listings[index].in_use) {
                    printf("This listing is not active\n");
                    break;
                }

                cnt = read(0, listings[index].listing->name, listings[index].listing->name_size);
                
                printf("Edited %d bytes at index %zu!\n", cnt, index);
                break;
            case 3:
                index = get_index();
                delete listings[index].listing;
                listings[index].in_use = false;
                printf("Deleted listing at index %zu!\n", index);
                break;
            case 4:
                index = get_index();
                if(!listings[index].in_use) {
                    printf("This listing is not active\n");
                    break;
                }

                listings[index].listing->ShowListing();
                break;
            case 5:
                printf("Goodbye!\n");
                exit(0);
            default:
                printf("Invalid choice.\n");
                break;
        }
    }
}