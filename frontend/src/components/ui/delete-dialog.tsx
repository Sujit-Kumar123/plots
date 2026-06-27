"use client"

import * as React from "react"
import { toast } from "sonner"
import { Spinner } from "@/components/ui/spinner"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

interface DeleteDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title?: string
  description?: React.ReactNode
  onConfirm: () => Promise<{ error?: string | null }>
  successMessage?: string
}

export function DeleteDialog({
  open,
  onOpenChange,
  title = "Delete?",
  description,
  onConfirm,
  successMessage,
}: DeleteDialogProps) {
  const [deleting, setDeleting] = React.useState(false)
  const [deleteError, setDeleteError] = React.useState<string | null>(null)

  function handleOpenChange(next: boolean) {
    if (!next) setDeleteError(null)
    onOpenChange(next)
  }

  async function handleDelete() {
    setDeleting(true)
    setDeleteError(null)

    const result = await onConfirm()

    setDeleting(false)

    if (result.error) {
      setDeleteError(result.error)
      toast.error(result.error)
      return
    }

    if (successMessage) toast.success(successMessage)
    onOpenChange(false)
  }

  return (
    <AlertDialog open={open} onOpenChange={handleOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          {description != null && (
            <AlertDialogDescription>{description}</AlertDialogDescription>
          )}
        </AlertDialogHeader>

        {deleteError && (
          <p className="text-sm text-destructive px-1">{deleteError}</p>
        )}

        <AlertDialogFooter>
          <AlertDialogCancel disabled={deleting}>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={handleDelete} disabled={deleting}>
            {deleting && <Spinner />}
            {deleting ? "Deleting…" : "Delete"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
