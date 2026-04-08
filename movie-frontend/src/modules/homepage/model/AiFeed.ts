import type { MovieHeroGetVm } from "./MovieHeroGetVm"
import type { Section } from "./Section"

export type AiFeed = {
    hero: MovieHeroGetVm,
    sections: Section[]
}