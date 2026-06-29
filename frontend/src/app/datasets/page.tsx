"use client";

import { useAppStore } from "@/store/app-store";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Database, Search, Filter, ArrowUpDown, ChevronLeft, ChevronRight } from "lucide-react";
import Link from "next/link";

export default function DatasetExplorer() {
  const datasetCache = useAppStore((state) => state.datasetCache);
  const datasets = Object.values(datasetCache);
  
  const [searchTerm, setSearchTerm] = useState("");
  const [sortField, setSortField] = useState<"filename" | "quality" | "rows">("filename");
  const [sortAsc, setSortAsc] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Search & Filter
  const filteredDatasets = datasets.filter((d) =>
    d.filename.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Sorting
  const sortedDatasets = [...filteredDatasets].sort((a, b) => {
    let valA: any = a.filename;
    let valB: any = b.filename;

    if (sortField === "quality") {
      valA = a.analysis?.quality?.quality_score || 0;
      valB = b.analysis?.quality?.quality_score || 0;
    } else if (sortField === "rows") {
      valA = a.analysis?.metadata?.rows || 0;
      valB = b.analysis?.metadata?.columns || 0;
    }

    if (valA < valB) return sortAsc ? -1 : 1;
    if (valA > valB) return sortAsc ? 1 : -1;
    return 0;
  });

  // Pagination
  const totalPages = Math.ceil(sortedDatasets.length / itemsPerPage);
  const paginatedDatasets = sortedDatasets.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const toggleSort = (field: typeof sortField) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dataset Explorer</h1>
          <p className="text-sm text-muted-foreground">
            Search, sort, filter, and review details of all uploaded datasets.
          </p>
        </div>
        <Link href="/upload">
          <Button className="rounded-full bg-primary hover:bg-primary/95 text-primary-foreground">Injest File</Button>
        </Link>
      </div>

      <Card className="rounded-xl border border-border">
        <CardHeader className="flex flex-col sm:flex-row items-center justify-between gap-4 pb-4">
          <div className="relative w-full sm:max-w-sm">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search datasets..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 rounded-lg"
            />
          </div>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Button variant="outline" size="sm" className="rounded-lg gap-1 text-xs">
              <Filter className="h-4 w-4" />
              Filter By
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {paginatedDatasets.length === 0 ? (
            <div className="text-center py-16 text-muted-foreground text-xs">
              <Database className="h-12 w-12 mx-auto text-muted-foreground/30 mb-2" />
              No datasets found matching your search.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-border text-muted-foreground font-semibold">
                    <th className="py-3 px-4">
                      <button
                        className="flex items-center gap-1 hover:text-foreground transition"
                        onClick={() => toggleSort("filename")}
                      >
                        Dataset Name <ArrowUpDown className="h-3.5 w-3.5" />
                      </button>
                    </th>
                    <th className="py-3 px-4">Size</th>
                    <th className="py-3 px-4">
                      <button
                        className="flex items-center gap-1 hover:text-foreground transition"
                        onClick={() => toggleSort("rows")}
                      >
                        Dimensions <ArrowUpDown className="h-3.5 w-3.5" />
                      </button>
                    </th>
                    <th className="py-3 px-4">
                      <button
                        className="flex items-center gap-1 hover:text-foreground transition"
                        onClick={() => toggleSort("quality")}
                      >
                        Quality Score <ArrowUpDown className="h-3.5 w-3.5" />
                      </button>
                    </th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedDatasets.map((d) => (
                    <tr
                      key={d.dataset_id}
                      className="border-b border-border hover:bg-accent/10 transition"
                    >
                      <td className="py-4 px-4 font-semibold max-w-xs truncate">
                        {d.filename}
                      </td>
                      <td className="py-4 px-4 text-muted-foreground">
                        {d.analysis?.metadata?.size_bytes
                          ? (d.analysis.metadata.size_bytes / 1024).toFixed(1) + " KB"
                          : "N/A"}
                      </td>
                      <td className="py-4 px-4 text-muted-foreground font-medium">
                        {d.analysis?.metadata?.rows} rows × {d.analysis?.metadata?.columns} cols
                      </td>
                      <td className="py-4 px-4">
                        <span className="font-bold text-primary">
                          {d.analysis?.quality?.quality_score}%
                        </span>
                      </td>
                      <td className="py-4 px-4">
                        <Badge variant="secondary" className="rounded-full text-[10px] uppercase font-bold">
                          {d.dataset_type || "Analyzed"}
                        </Badge>
                      </td>
                      <td className="py-4 px-4">
                        <Link href={`/datasets/${d.dataset_id}`}>
                          <Button size="sm" variant="outline" className="h-8 rounded-lg">
                            Inspect
                          </Button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination Footer */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-4 text-xs text-muted-foreground border-t border-border mt-4">
              <span>
                Showing {(currentPage - 1) * itemsPerPage + 1} to{" "}
                {Math.min(currentPage * itemsPerPage, sortedDatasets.length)} of{" "}
                {sortedDatasets.length} datasets
              </span>
              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 rounded-lg"
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="font-semibold text-foreground px-2">
                  Page {currentPage} of {totalPages}
                </span>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 rounded-lg"
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
