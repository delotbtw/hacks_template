import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'

import { api } from '@/api/client'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

function HealthCard() {
  const { data, isError } = useQuery({
    queryKey: ['health'],
    queryFn: async () => (await api.GET('/health')).data,
    refetchInterval: 10_000,
  })
  return (
    <Card>
      <CardHeader>
        <CardTitle>Статус API</CardTitle>
      </CardHeader>
      <CardContent className="text-sm">
        {isError || !data ? 'недоступен' : `${data.status} (db: ${data.db}, redis: ${data.redis})`}
      </CardContent>
    </Card>
  )
}

function Items() {
  const qc = useQueryClient()
  const [name, setName] = useState('')
  const { data: items = [] } = useQuery({
    queryKey: ['items'],
    queryFn: async () => (await api.GET('/items')).data ?? [],
  })
  const create = useMutation({
    mutationFn: (n: string) => api.POST('/items', { body: { name: n } }),
    onSuccess: () => {
      setName('')
      return qc.invalidateQueries({ queryKey: ['items'] })
    },
  })
  const submit = (e: FormEvent) => {
    e.preventDefault()
    if (name.trim()) create.mutate(name.trim())
  }
  return (
    <Card>
      <CardHeader>
        <CardTitle>Items</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={submit} className="flex gap-2">
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Название" />
          <Button type="submit" disabled={create.isPending}>
            Добавить
          </Button>
        </form>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Название</TableHead>
              <TableHead>Создан</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.map((i) => (
              <TableRow key={i.id}>
                <TableCell>{i.id}</TableCell>
                <TableCell>{i.name}</TableCell>
                <TableCell>{new Date(i.created_at).toLocaleString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

export default function App() {
  return (
    <main className="mx-auto max-w-2xl space-y-4 p-6">
      <HealthCard />
      <Items />
    </main>
  )
}
