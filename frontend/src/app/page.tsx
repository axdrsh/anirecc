"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2 } from "lucide-react"
import axios from 'axios';

interface Recommendation {
  title: string;
  synopsis: string;
  image_url: string;
  mal_id: number;
  score: string;
  episodes: number;
}

export default function AnimeRecommender() {
  const [selectedMood, setSelectedMood] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null)
  const [error, setError] = useState<string | null>(null)

  const moods = [
    "happy",
    "sad",
    "excited",
    "chill",
    "romantic",
    "nostalgic",
    "adventurous",
    "mysterious",
    "thoughtful",
    "energetic",
    "relaxed",
    "melancholic",
    "inspired",
    "anxious",
    "determined",
  ]

  const handleMoodClick = async (mood: string) => {
    setSelectedMood(mood)
    setLoading(true)
    setError(null)
    setRecommendation(null)

    try {
      const response = await axios.post('http://127.0.0.1:5000/recommend', { mood })
      setRecommendation(response.data.recommendation)
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.error || 'Failed to fetch recommendation')
      } else {
        setError('An unexpected error occurred')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 bg-background">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold">anirecc</h1>
          <p className="text-muted-foreground mt-2">select your mood to get an anime recommendation</p>
        </div>

        <div className="grid grid-cols-3 sm:grid-cols-5 gap-2 justify-center">
          {moods.map((mood) => (
            <Button
              key={mood}
              variant={selectedMood === mood ? "default" : "outline"}
              onClick={() => handleMoodClick(mood)}
              className="capitalize"
            >
              {mood}
            </Button>
          ))}
        </div>

        {loading && (
          <div className="flex justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        )}

        {error && !loading && (
          <Card className="border-destructive">
            <CardHeader>
              <CardTitle className="text-destructive">Error</CardTitle>
            </CardHeader>
            <CardContent>
              <p>{error}</p>
            </CardContent>
            <CardFooter>
              <Button
                variant="outline"
                className="w-full"
                onClick={() => {
                  setSelectedMood(null)
                  setError(null)
                }}
              >
                Try again
              </Button>
            </CardFooter>
          </Card>
        )}

        {recommendation && !loading && !error && (
          <Card>
            <CardHeader>
              <CardTitle>{recommendation.title}</CardTitle>
              <CardDescription>
                Score: {recommendation.score} • Episodes: {recommendation.episodes}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="aspect-video w-full overflow-hidden rounded-md mb-4">
                <img
                  src={recommendation.image_url || "/placeholder.svg"}
                  alt={recommendation.title}
                  className="object-cover w-full h-full"
                />
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
             
              <Button
                variant="outline"
                className="w-full"
                onClick={() => window.open(`https://myanimelist.net/anime/${recommendation.mal_id}`, '_blank')}
              >
                View on MAL
              </Button>
            </CardFooter>
          </Card>
        )}
      </div>
    </main>
  )
}