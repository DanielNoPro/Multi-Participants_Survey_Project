import api from "@/constants/api"

export const questionService = {
    getQuestions(page) {
        return api.get(`/api/v1/questions/?page=${page}&page_size=10`)
    },

    getQuestionTypes() {
        return api.get('/api/v1/question_types/')
    },

    createQuestion(data) {
        return api.post('/api/v1/questions/', data)
    },

    deleteQuestion(id) {
        return api.delete(`/api/v1/questions/${id}`)
    },

    getQuestionDetail(id) {
        return api.get(`/api/v1/questions/${id}`)
    },

    // updateQuestion(id, data) {
    //     return api.put(`/api/v1/questions/${id}/`, data)
    // },

    updateQuestion(id, data) {
        return api.patch(`/api/v1/questions/${id}/`, data)
    },

    deleteQuestionOption(question_id, option_id) {
        return api.delete(`/api/v1/questions/${question_id}/options/${option_id}/`)
    },

    getQuestionOptions(id) {
        return api.get(`/api/v1/questions/${id}/options/`)
    },

    updateQuestionOption(question_id, option_id, data) {
        return api.put(`/api/v1/questions/${question_id}/options/${option_id}/`, data)
    },

    createQuestionOption(question_id, data) {
        return api.post(`/api/v1/questions/${question_id}/options/`, data)
    }
}
