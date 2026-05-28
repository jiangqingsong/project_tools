import axios from 'axios'

const api = axios.create({ baseURL: '/api/office' })

export async function pdfToWord(file: File) {
  const form = new FormData()
  form.append('file', file)
  const res = await api.post('/pdf/to-word', form, { responseType: 'blob' })
  return res.data
}

export async function pdfMerge(files: File[]) {
  const form = new FormData()
  files.forEach(f => form.append('files', f))
  const res = await api.post('/pdf/merge', form, { responseType: 'blob' })
  return res.data
}

export async function pdfSplit(file: File, mode: string, pages: string) {
  const form = new FormData()
  form.append('file', file)
  form.append('mode', mode)
  form.append('pages', pages)
  const res = await api.post('/pdf/split', form, { responseType: 'blob' })
  return res.data
}

export async function pdfToImage(file: File, fmt: string = 'png') {
  const form = new FormData()
  form.append('file', file)
  form.append('fmt', fmt)
  const res = await api.post('/pdf/to-image', form, { responseType: 'blob' })
  return res.data
}

export async function wordToPdf(file: File) {
  const form = new FormData()
  form.append('file', file)
  const res = await api.post('/convert/word-to-pdf', form, { responseType: 'blob' })
  return res.data
}

export async function markdownConvert(text: string, outputFormat: string, file?: File) {
  const form = new FormData()
  form.append('output_format', outputFormat)
  if (file) {
    form.append('file', file)
  } else {
    form.append('text', text)
  }
  const res = await api.post('/convert/markdown', form, { responseType: 'blob' })
  return res.data
}
