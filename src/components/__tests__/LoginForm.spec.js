import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LoginForm from '../LoginForm.vue'

describe('LoginForm', () => {
  it('rendert ohne Fehler', () => {
    const wrapper = mount(LoginForm)
    expect(wrapper.exists()).toBe(true)
  })
})