import { useState, useRef } from "react"
import { UploadCloudIcon } from "lucide-react"

export default function UploadBox({ onFileSelected, isLoading }) {
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef(null)

  function handleDrop(e) {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) onFileSelected(file)
  }

  function handleChange(e) {
    const file = e.target.files[0]
    if (file) onFileSelected(file)
  }

  return (
    <div
      onClick={() => !isLoading && inputRef.current.click()}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={`
        specimen-frame border-2 border-dashed p-12
        flex flex-col items-center justify-center gap-4
        cursor-pointer transition-all select-none
        ${isDragging
          ? "border-accent bg-accent/5"
          : "border-border hover:border-secondary bg-surface"
        }
        ${isLoading ? "opacity-40 cursor-not-allowed" : ""}
      `}
    >
      <UploadCloudIcon size={36} className="text-muted" />
      <div className="text-center">
        <p className="font-medium text-primary">Drop an image here</p>
        <p className="text-sm text-secondary mt-1">or click to browse — JPEG, PNG, WebP</p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={handleChange}
        disabled={isLoading}
      />
    </div>
  )
}
