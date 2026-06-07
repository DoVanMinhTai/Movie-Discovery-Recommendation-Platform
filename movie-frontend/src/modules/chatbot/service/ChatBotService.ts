import apiClientService from "../../../common/services/ApiClientService";
import { API_ENDPOINTS } from "../../../constants/ApiEndpoints";
import type { ChatPostVm } from "../model/ChatPostVm";

export async function sendMessage(chatPostVm: ChatPostVm) {
    const response = await apiClientService.post(API_ENDPOINTS.CHATBOT.MESSAGE, chatPostVm);
    return response;
}