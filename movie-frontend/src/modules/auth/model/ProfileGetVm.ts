import type { ROLE_TYPE } from "./enum/ROLE";

export type ProfileGetVm = {
    id: number;
    userName: string;
    token: string;
    fullName: string;
    email: string;
    role: ROLE_TYPE;
    joinedDate: string;
    preferences: string[];
};