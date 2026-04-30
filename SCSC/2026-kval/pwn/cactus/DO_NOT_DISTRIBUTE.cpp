
/// IMPORTANT:
/// THIS FILE SHOULD NOT BE DISTRIBUTED TO COMPETITORS
/// MEANT TO BE PWN/REV

/// TO COMPILE:
/// g++ main.cpp -static -std=c++20 -o main

#include <iostream>
#include <unordered_map>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <random>
#include <type_traits>
#include <thread>
#include <chrono>

std::minstd_rand rng(1337);

class PageMap {
  private:
    std::array<uint16_t, 0x100> map;
  public:
    uint16_t get_offset_tag(uint16_t offset) {
      offset &= 0xff0;
      int32_t idx = offset / 0x10;
      return map[idx];
    }
    void set_offset_tag(uint16_t offset, uint16_t val) {
      offset &= 0xff0;
      size_t idx = offset / 0x10;
      map[idx] = val;
    }
};

std::unordered_map<unsigned long, PageMap> mte;

template <typename T>
class MagicPtr {
  private:
    uintptr_t ptr;
    T* get_pointer() const {
      return reinterpret_cast<T*>(ptr & ~uintptr_t(0xffff000000000000));
    }
    uint16_t get_key() const {
      return static_cast<uint16_t>(ptr >> 48);
    }
  public:
    using element_type = std::remove_extent_t<T>;
    MagicPtr() {
      uint16_t key = rng();
      size_t n_chunks = (sizeof(T)+0xf)/0x10;
      T* pointer = new T;
      this->ptr = (uintptr_t(key) << 48 | reinterpret_cast<uintptr_t>(pointer));

      const uintptr_t base = reinterpret_cast<uintptr_t>(pointer);
      for(int i = 0; i < n_chunks; i++) {
        uintptr_t chunk = base + i*0x10;
        uintptr_t page = chunk >> 12;
        if (mte.count(chunk >> 12) == 0)
          mte[page] = PageMap();

        mte[page].set_offset_tag(static_cast<uint16_t>(chunk), key);
      }
    }
    ~MagicPtr() {
      uint16_t key = rng();
      size_t n_chunks = (sizeof(T)+0xf)/0x10;

      const uintptr_t base = reinterpret_cast<uintptr_t>(get_pointer());
      for(int i = 0; i < n_chunks; i++) {
        uintptr_t chunk = base + i*0x10;
        uintptr_t page = chunk >> 12;
        if (mte.count(page) == 0) {
          std::cerr << "Memory Integrity Error!\n";
          std::abort();
        }

        if (mte[page].get_offset_tag(static_cast<uint16_t>(chunk)) != get_key()) {
          std::cerr << "Memory Integrity Error!\n";
          std::abort();
        }

        mte[page].set_offset_tag(static_cast<uint16_t>(chunk), key);
      }
      delete get_pointer();
    }
    T& operator*() {
      size_t n_chunks = (sizeof(T)+0xf)/0x10;
      uint16_t key = get_key();

      const uintptr_t base = reinterpret_cast<uintptr_t>(get_pointer());
      for(int i = 0; i < n_chunks; i++) {
        uintptr_t chunk = base + i*0x10;
        uintptr_t page = chunk >> 12;
        if (mte.count(page) == 0) {
          std::cerr << "Memory Integrity Error!\n";
          std::abort();
        }

        if (mte[page].get_offset_tag(static_cast<uint16_t>(chunk)) != key) {
          std::cerr << "Memory Integrity Error!\n";
          std::abort();
        }
      }

      return *get_pointer();
    }
};


void menu() {
  std::cout << "============\n";
  std::cout << "1. Add Note\n";
  std::cout << "2. Delete Note\n";
  std::cout << "3. Write Note\n";
  std::cout << "4. Read Note\n";
  std::cout << "5. Exit\n";
  std::cout << "============\n";
  std::cout << "\n\n > ";
}

std::array<MagicPtr<long>, 0x20> notes;

void add_note() {
  int idx;
  std::cout << "Which? ";
  std::cin >> idx;
  std::construct_at(&notes.at(idx));
  *notes.at(idx) = 0;
}

void delete_note() {
  int idx;
  std::cout << "Which? ";
  std::cin >> idx;
  std::destroy_at(&notes.at(idx));
}
void write_note() {
  int idx;
  std::cout << "Which? ";
  std::cin >> idx;
  std::cout << "Ok: ";
  std::cin >> *notes.at(idx);
}
void read_note() {
  int idx;
  std::cout << "Which? ";
  std::cin >> idx;
  std::cout << *notes.at(idx) << "\n";
}

int main() {
  std::ios::sync_with_stdio(false);
  std::cin.tie(nullptr);
  std::cout.setf(std::ios::unitbuf);

  std::thread([](){
      std::this_thread::sleep_for(std::chrono::seconds(5));
      std::exit(0);
  }).detach();

  std::array<void (*)(), 4> options = {
    add_note, delete_note, write_note, read_note
  };

  while(true) {
    size_t command;
    menu();
    std::cin >> command;
    command--;
    if (command == options.size())
      exit(0);
    options.at(command)();
  }

  return 0;
}
