<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 selection:bg-indigo-500 selection:text-white">
    <!-- Background Glow Effect -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-gradient-to-tr from-indigo-600/20 via-violet-600/10 to-transparent blur-3xl rounded-full"></div>
    </div>

    <div class="relative max-w-5xl mx-auto px-4 py-10 sm:py-14">
      
      <!-- Top Header -->
      <header class="text-center mb-10">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs text-indigo-400 font-medium mb-4 shadow-inner">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          AI Vision Retrieval &bull; Qdrant Vector Engine
        </div>
        <h1 class="text-3xl sm:text-5xl font-extrabold tracking-tight bg-gradient-to-b from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
          ระบบระบุรุ่นอุปกรณ์ไอทีด้วยภาพ
        </h1>
        <p class="text-slate-400 mt-3 text-sm sm:text-base max-w-xl mx-auto">
          วิเคราะห์รูปทรง โครงสร้างปุ่ม และอัตลักษณ์ของอุปกรณ์ เพื่อระบุรุ่นที่ถูกต้องทันที
        </p>
      </header>

      <!-- Main Upload Area -->
      <div class="bg-slate-900/80 backdrop-blur-md border border-slate-800/80 rounded-3xl p-6 sm:p-8 shadow-2xl mb-10">
        
        <div 
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
          :class="[
            'relative group border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center cursor-pointer transition-all duration-300',
            isDragging 
              ? 'border-indigo-500 bg-indigo-950/30 scale-[0.99]' 
              : 'border-slate-700/80 hover:border-indigo-500/70 bg-slate-950/40 hover:bg-slate-950/60'
          ]"
        >
          <input 
            type="file" 
            ref="fileInputRef" 
            accept="image/*" 
            class="hidden" 
            @change="handleFileSelect"
          />

          <!-- ยังไม่ได้เลือกรูป -->
          <div v-if="!imagePreview" class="flex flex-col items-center">
            <div class="w-16 h-16 rounded-2xl bg-indigo-950/50 border border-indigo-800/50 flex items-center justify-center text-indigo-400 mb-4 group-hover:scale-110 transition-transform">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
            </div>
            <p class="text-base font-semibold text-slate-200">
              ลากรูปภาพมาวางที่นี่ หรือ <span class="text-indigo-400 underline decoration-indigo-400/50 underline-offset-4">เลือกไฟล์จากเครื่อง</span>
            </p>
            <p class="text-xs text-slate-500 mt-2">รองรับรูปถ่าย PNG, JPG, WebP ทุกมุมมอง</p>
          </div>

          <!-- พรีวิวรูปภาพที่เลือก -->
          <div v-else class="relative group/preview">
            <img 
              :src="imagePreview" 
              alt="Uploaded Preview" 
              class="max-h-72 mx-auto rounded-xl shadow-2xl object-contain border border-slate-700 cursor-zoom-in"
              @click.stop="openModal(imagePreview, 'รูปภาพที่คุณอัปโหลด')"
            />
            <div class="mt-4 flex items-center justify-center gap-3">
              <button 
                type="button" 
                @click.stop="openModal(imagePreview, 'รูปภาพที่คุณอัปโหลด')"
                class="px-3.5 py-1.5 rounded-full bg-slate-800 hover:bg-slate-700 text-xs text-indigo-300 font-medium transition flex items-center gap-1.5"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"></path>
                </svg>
                ดูภาพขนาดเต็ม
              </button>
              <button 
                type="button" 
                @click.stop="triggerFileInput" 
                class="px-3.5 py-1.5 rounded-full bg-slate-800/80 hover:bg-slate-700 text-xs text-slate-300 font-medium transition"
              >
                เปลี่ยนรูปภาพ
              </button>
            </div>
          </div>
        </div>

        <!-- ปุ่ม Action -->
        <button 
          @click="searchDevice"
          :disabled="!selectedFile || isLoading"
          class="w-full mt-6 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium py-3.5 rounded-xl shadow-lg shadow-indigo-600/20 transition duration-200 flex justify-center items-center gap-2"
        >
          <svg v-if="isLoading" class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
          </svg>
          <span class="text-sm font-semibold tracking-wide">
            {{ isLoading ? 'AI กำลังประมวลผลค้นหารุ่น...' : 'ระบุรุ่นอุปกรณ์' }}
          </span>
        </button>
      </div>

      <!-- Result Showcase -->
      <div v-if="matches.length > 0 && !isLoading" class="space-y-6">
        
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold text-slate-100 flex items-center gap-2">
            <span>🎯 ผลลัพธ์การระบุรุ่นอุปกรณ์</span>
          </h2>
        </div>

        <!-- รายการการ์ดผลลัพธ์ เรียง 1 -> 2 -> 3 -->
        <div class="grid gap-4">
          <div 
            v-for="(item, index) in matches" 
            :key="index"
            :class="[
              'rounded-2xl border transition-all duration-300 overflow-hidden',
              index === 0 
                ? 'bg-slate-900/90 border-indigo-500/80 shadow-2xl shadow-indigo-950/60 ring-1 ring-indigo-500/30' 
                : 'bg-slate-900/40 border-slate-800/80 hover:border-slate-700'
            ]"
          >
            <div class="p-5 sm:p-6">
              
              <!-- Tag หัวการ์ด ระบุอันดับชัดเจน -->
              <div class="flex items-center justify-between mb-4">
                <span 
                  :class="[
                    'text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider flex items-center gap-1.5',
                    index === 0 
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/40' 
                      : 'bg-slate-800 text-slate-400'
                  ]"
                >
                  <span v-if="index === 0">★</span>
                  <span>อันดับ {{ index + 1 }}</span>
                  <span v-if="index === 0" class="text-indigo-200 font-normal">| รุ่นที่ตรงที่สุด</span>
                </span>
              </div>

              <!-- Content Body: รูปสินค้า + รายละเอียด -->
              <div class="flex flex-col md:flex-row gap-6 items-center">
                
                <!-- กล่องรูปภาพจาก Database (คลิกดูขนาดเต็มได้) -->
                <div class="relative group/img w-full md:w-52 h-44 bg-slate-950/80 rounded-xl overflow-hidden border border-slate-800 flex items-center justify-center p-2 shrink-0">
                  <img 
                    v-if="item.image_url" 
                    :src="item.image_url" 
                    :alt="item.display_name"
                    class="w-full h-full object-contain cursor-zoom-in group-hover/img:scale-105 transition duration-300"
                    loading="lazy"
                    @click="openModal(item.image_url, item.display_name)"
                  />
                  <span v-else class="text-xs text-slate-500">ไม่มีรูปภาพ</span>

                  <div 
                    v-if="item.image_url" 
                    @click="openModal(item.image_url, item.display_name)"
                    class="absolute inset-0 bg-slate-950/60 opacity-0 group-hover/img:opacity-100 transition-opacity flex flex-col items-center justify-center gap-1 cursor-pointer"
                  >
                    <svg class="w-6 h-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"></path>
                    </svg>
                    <span class="text-xs text-white font-medium">กดเพื่อขยาย</span>
                  </div>
                </div>

                <!-- รายละเอียดชื่อรุ่น -->
                <div class="flex-1 w-full space-y-3">
                  <h3 :class="['font-bold text-slate-100 leading-snug', index === 0 ? 'text-lg sm:text-xl text-indigo-100' : 'text-base']">
                    {{ item.display_name }}
                  </h3>

                  <div class="flex flex-wrap items-center gap-2 text-xs">
                    <span class="bg-slate-800/70 text-slate-400 px-2.5 py-1 rounded-md border border-slate-700/50 truncate max-w-xs">
                      ไฟล์: {{ item.filename }}
                    </span>
                    
                    <button 
                      v-if="item.image_url"
                      type="button"
                      @click="openModal(item.image_url, item.display_name)"
                      class="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-indigo-950/70 hover:bg-indigo-900 border border-indigo-700/50 text-indigo-300 font-medium transition"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                      </svg>
                      ดูภาพสินค้าขนาดเต็ม
                    </button>
                  </div>
                </div>

              </div>

            </div>
          </div>
        </div>

      </div>

    </div>

    <!-- Image Lightbox Modal -->
    <div 
      v-if="modalImage" 
      class="fixed inset-0 z-50 bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 transition-all"
      @click.self="closeModal"
    >
      <div class="relative max-w-4xl w-full bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
        
        <div class="flex items-center justify-between px-5 py-3.5 border-b border-slate-800 bg-slate-900/90">
          <h4 class="text-sm font-semibold text-slate-200 truncate pr-4">
            {{ modalTitle }}
          </h4>
          <button 
            @click="closeModal" 
            class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center transition"
          >
            ✕
          </button>
        </div>

        <div class="p-4 flex items-center justify-center overflow-auto bg-slate-950/50">
          <img 
            :src="modalImage" 
            :alt="modalTitle" 
            class="max-h-[72vh] w-auto max-w-full rounded-lg object-contain shadow-lg"
          />
        </div>

        <div class="px-5 py-3 border-t border-slate-800/80 bg-slate-900/60 flex items-center justify-between text-xs text-slate-400">
          <span>กดที่พื้นหลัง หรือปุ่ม ✕ เพื่อปิด</span>
          <a 
            :href="modalImage" 
            target="_blank" 
            rel="noopener noreferrer"
            class="text-indigo-400 hover:underline inline-flex items-center gap-1"
          >
            เปิดในแท็บใหม่ ↗
          </a>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const fileInputRef = ref(null)
const selectedFile = ref(null)
const imagePreview = ref(null)
const isDragging = ref(false)
const isLoading = ref(false)
const matches = ref([])

const modalImage = ref(null)
const modalTitle = ref('')

const openModal = (url, title) => {
  modalImage.value = url
  modalTitle.value = title || 'รูปภาพอุปกรณ์'
}

const closeModal = () => {
  modalImage.value = null
  modalTitle.value = ''
}

const handleKeydown = (e) => {
  if (e.key === 'Escape' && modalImage.value) {
    closeModal()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

const triggerFileInput = () => {
  fileInputRef.value.click()
}

const processFile = (file) => {
  if (!file || !file.type.startsWith('image/')) return
  selectedFile.value = file
  matches.value = []
  
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  processFile(file)
}

const handleDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  processFile(file)
}

const searchDevice = async () => {
  if (!selectedFile.value) return

  isLoading.value = true
  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const response = await fetch('http://127.0.0.1:8000/api/search', {
      method: 'POST',
      body: formData
    })
    const data = await response.json()
    matches.value = data.matches || []
  } catch (error) {
    console.error('Search error:', error)
    alert('ไม่สามารถเชื่อมต่อกับ Backend ได้ กรุณาตรวจสอบว่า python app.py รันอยู่หรือไม่')
  } finally {
    isLoading.value = false
  }
}
</script>