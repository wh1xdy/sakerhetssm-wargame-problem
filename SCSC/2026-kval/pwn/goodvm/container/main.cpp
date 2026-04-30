#include <cstdint>
#include <cstring>
#include <exception>
#include <iostream>
#include <sys/mman.h>
#include <unordered_map>
#include <vector>

#define PAGE_SIZE 0x1000
#define PAGE_SHIFT 12
#define PAGE_COUNT(n) ((n + PAGE_SIZE - 1) >> PAGE_SHIFT)

#define MAX_PAGE_ALLOC (1 << 22)
#define N_SYSCALLS 3

class PageTable {
private:
  std::unordered_map<long, long> map;

public:
  long virt_to_phys(long virt) {
    try {
      long phys_page = map.at(virt >> PAGE_SHIFT) << PAGE_SHIFT;
      return phys_page | (virt & 0xfff);
    } catch (std::out_of_range &err) {
      throw std::runtime_error("vm pagefault\n");
    }
  }

  void create_map(long phys, long virt) {
    map[virt >> PAGE_SHIFT] = phys >> PAGE_SHIFT;
  }

  bool is_mapped(long virt) { return map.count(virt >> 12) != 0; }
};

class GoodVM {
private:
  PageTable pt;
  long registers[16] = {};

  void VM_read() {
    long buf = registers[1];
    long n = registers[2];
    registers[0] = n;
    std::cin.read((char *)pt.virt_to_phys(buf), n);
  };

  void VM_write() {
    long buf = registers[1];
    long n = registers[2];
    registers[0] = n;
    while (n--)
      std::cout << *(uint8_t *)pt.virt_to_phys(buf++);
  }

  void VM_mmap() {
    long hint = registers[1];
    long size = PAGE_COUNT(registers[2]) * PAGE_SIZE;
    registers[0] = 0;
    if (size == 0)
      return;
    if ((hint & 0xfff) != 0)
      return;
    for (int i = 0; i < PAGE_COUNT(registers[2]); i++) {
      if (pt.is_mapped(hint + PAGE_SIZE * i))
        return;
    }
    for (int i = 0; i < PAGE_COUNT(registers[2]); i++) {
      void *pg = mmap(NULL, 0x1000, PROT_READ | PROT_WRITE | PROT_EXEC,
                      MAP_PRIVATE | MAP_ANONYMOUS, 0, 0);
      if (pg == MAP_FAILED)
        throw std::runtime_error("failed mmap");
      pt.create_map((long)pg, hint + PAGE_SIZE * i);
    }
    registers[0] = hint;
  }

  std::vector<void (GoodVM::*)()> syscalls = {
      &GoodVM::VM_read, &GoodVM::VM_write, &GoodVM::VM_mmap};

  void alloc_pages(long size, long vaddr) {
    if (size == 0 || size > MAX_PAGE_ALLOC)
      throw(std::invalid_argument("too much"));

    void *pages =
        mmap(NULL, PAGE_COUNT(size) * PAGE_SIZE, PROT_READ | PROT_WRITE,
             MAP_PRIVATE | MAP_ANONYMOUS, 0, 0);
    if (pages == MAP_FAILED)
      throw(std::bad_alloc());

    for (int i = 0; i < PAGE_COUNT(size); i++) {
      pt.create_map((long)((uint8_t *)pages + PAGE_SIZE * i),
                    vaddr + PAGE_SIZE * i);
    }
  }

  void copy_to_pages(long vaddr, long size, void *stuff) {
    if (vaddr & 0xfff)
      throw(std::invalid_argument("unaligned"));
    int n_pages = PAGE_COUNT(size);
    int full_pages = size >> PAGE_SHIFT;

    for (int i = 0; i < full_pages; i++) {
      memcpy((void *)pt.virt_to_phys(vaddr + i * PAGE_SIZE),
             (uint8_t *)stuff + i * PAGE_SIZE, 0x1000);
    }

    if (full_pages < n_pages)
      memcpy((void *)pt.virt_to_phys(vaddr + PAGE_SIZE * full_pages),
             (uint8_t *)stuff + PAGE_SIZE * full_pages, size & 0xfff);
  }

  uint8_t read_byte(long vaddr) { return *(uint8_t *)pt.virt_to_phys(vaddr); }
  uint16_t read_short(long vaddr) {
    if (vaddr & 1)
      throw std::runtime_error("vm sigbus");
    return *(uint16_t *)pt.virt_to_phys(vaddr);
  }
  uint64_t read_long(long vaddr) {
    if (vaddr & 7)
      throw std::runtime_error("vm sigbus");
    return *(uint64_t *)pt.virt_to_phys(vaddr);
  }
  void write_long(long vaddr, uint64_t val) {
    if (vaddr & 7)
      throw std::runtime_error("vm sigbus");
    *(uint64_t *)pt.virt_to_phys(vaddr) = val;
  }

public:
  GoodVM(std::vector<uint8_t> code) {
    alloc_pages(code.size(), 0);
    alloc_pages(0x8000, 0x7f0000000);

    copy_to_pages(0, code.size(), code.data());
    registers[0xe] = 0x7f0008000 - 8;
    registers[0xf] = 0;
  }
  void run() {
    while (true) {
      try {
        step();
      } catch (std::runtime_error &err) {
        std::cerr << "vm error: " << err.what() << "\n";
        exit(1);
      }
    }
  }

  void step() {
    uint64_t ins = read_long(registers[0xf]);
    uint8_t op = ins & 0xff;
    uint8_t rx = (ins >> 8) & 0xf;
    uint8_t ry = (ins >> 12) & 0xf;

    switch (op >> 4) {
    case 0x1: {
      rx = op & 0xf;
      registers[0xe] -= 8;
      write_long(registers[0xe], registers[rx]);
      registers[0xf] += 8;
      break;
    }

    case 0x2: {
      rx = op & 0xf;
      registers[rx] = read_long(registers[0xe]);
      registers[0xe] += 8;

      if (rx != 0xf) {
        registers[0xf] += 8;
      }
      break;
    }

    case 0x3: {
      switch (op) {
      case 0x30:
        registers[1] = registers[rx] + registers[ry];
        break;
      case 0x31:
        registers[1] = registers[rx] - registers[ry];
        break;
      case 0x32:
        registers[1] = registers[rx] * registers[ry];
        break;
      case 0x33:
        if (!registers[ry])
          throw std::runtime_error("division by 0");
        registers[1] = registers[rx] / registers[ry];
        break;
      case 0x34:
        write_long(registers[rx], registers[ry]);
        break;
      case 0x35:
        registers[rx] = read_long(registers[ry]);
        break;
      case 0x36:
        std::swap(registers[rx], registers[ry]);
        break;
      default:
        throw std::runtime_error("invalid opcode");
      }
      registers[0xf] += 8;
      break;
    }

    case 0x4: {
      switch (op) {
      case 0x40:
        registers[0xf] = registers[rx];
        break;

      case 0x41:
        registers[0xe] -= 8;
        write_long(registers[0xe], registers[0xf] + 8);
        registers[0xf] = registers[rx];
        break;

      case 0x42:
        if (registers[rx] != 0)
          registers[0xf] = registers[rx];
        else
          registers[0xf] += 8;
        break;

      case 0x43: {
        registers[0xf] += 8;
        short rz = read_short(registers[0xf]);
        if (registers[rz] > registers[ry])
          registers[0xf] = registers[rx];
        else
          registers[0xf] += 8;
        break;
      }

      default:
        throw std::runtime_error("invalid opcode");
      }
      break;
    }

    case 0x5: {
      switch (op) {
      case 0x50: {
        registers[0xf] += 8;
        uint64_t imm = read_long(registers[0xf]);
        registers[0xf] += 8;
        registers[0xe] -= 8;
        write_long(registers[0xe], imm);
        break;
      }
      default:
        throw std::runtime_error("invalid opcode ");
      }
      break;
    }

    case 0xf: {
      switch (op) {
      case 0xff:
        registers[0xf] += 8;
        if (registers[0] >= N_SYSCALLS)
          throw std::runtime_error("invalid syscall");
        (this->*syscalls[registers[0]])();
        break;
      default:
        throw std::runtime_error("invalid opcode");
      }
      break;
    }

    default:
      throw std::runtime_error("invalid opcode");
    }
  }
};

int main() {
  std::vector<uint8_t> bytecode;
  bytecode.resize(4096);
  std::cout << "Welcome to GoodVM" << std::endl;
  std::cin.read((char *)bytecode.data(), 4096);

  GoodVM *vm = new GoodVM(bytecode);
  vm->run();
  return 0;
}
